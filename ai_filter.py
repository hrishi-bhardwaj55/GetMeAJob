"""
ai_filter.py - Uses OpenAI API (gpt-4o-mini) to evaluate jobs.
Provides structured metadata extraction and intelligent filtering.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
import openai
from filter import _fetch_description_in_thread

class JobEvaluation(BaseModel):
    is_match: bool = Field(description="True if the job passes the criteria and contains NO excluded terms.")
    match_score: int = Field(description="0 to 100 score representing how strong a fit this role is.")
    rejection_reason: str = Field(description="'N/A' if it's a match, else a highly specific reason for rejection.")
    missing_from_resume: str = Field(description="List of skills or experiences the job requires that are NOT present in the candidate's resume (e.g. 'Requires Angular and 8 years experience'). Put 'None' if they are a perfect match.")
    salary_range: Optional[str] = Field(description="The extracted raw salary range (e.g. '$150k - $200k') or null if none is mentioned.")
    experience_required: Optional[str] = Field(description="Extracted experience requirement (e.g. '3-5 years') or null.")
    tech_stack: List[str] = Field(description="List of core languages, tools, frameworks mentioned (e.g. 'Python', 'AWS').")
    job_summary: str = Field(description="A concise 1 or 2 sentence summary of the role designed to be read in a Discord alert.")

class AiFilterAgent:
    def __init__(self, criteria_dict: dict, max_workers: int = 5, api_key: str = ""):
        self.criteria = criteria_dict
        self.max_workers = max_workers
        self.client = openai.OpenAI(api_key=api_key) if api_key else None
        self.model_name = "gpt-4o-mini" # Fast, cheap, excellent at structured parsing

    def _evaluate_one(self, job):
        """Evaluates a single job using the AI model, returning the job and a proxy score."""
        description = _fetch_description_in_thread(job.application_link)
        job.description = description

        if not description:
            print(f"[AiFilter] ⚠️ Couldn't fetch description for {job.title} @ {job.company} — passing through.")
            job.description = "Description unavailable"
            job.parsed_salary = None
            job.parsed_experience = None
            job.parsed_skills = []
            job.job_summary = "Could not fetch details."
            return job, 100.0

        if not self.client:
            print("[AiFilter] ❌ OPENAI_API_KEY not provided. Bypassing AI evaluation.")
            return job, 100.0

        # Build prompt
        req_skills = self.criteria.get("required_skills", [])
        pref_skills = self.criteria.get("preferred_skills", [])
        exclusions = self.criteria.get("excluded_terms", [])
        
        from config import USER_RESUME
        
        system_prompt = "You are an AI Career Advisor helping a candidate apply to jobs. Your goal is to extract details and provide a gap analysis. You DO NOT gatekeep or reject jobs unless they violate strict exclusions."
        
        user_prompt = f"""
        Evaluate the following Job Description for a {job.title} role at {job.company}.
        
        CANDIDATE RESUME / PROFILE:
        {USER_RESUME}
        
        CRITERIA FLAGS:
        - Additional Required Skills: {', '.join(req_skills) if req_skills else 'None'}
        - Additional Preferred Skills: {', '.join(pref_skills) if pref_skills else 'None'}
        - STRICT Excluded Terms/Red Flags: {', '.join(exclusions) if exclusions else 'None'}
        
        ABSOLUTE RULES FOR APPROVAL (is_match):
        1. THE ONLY REASON TO REJECT: You MUST set `is_match = False` ONLY if the job description EXPLICITLY AND LITERALLY mentions ANY of the STRICT Excluded Terms (e.g., 'US Citizen', 'Clearance Required', 'Internship', 'Part time').
        2. DO NOT INFER CITIZENSHIP: If a job says "Must be legally authorized to work in the US", that DOES NOT mean "US Citizen Only". Do NOT reject the job unless it says "US Citizen ONLY" or "No Corp-to-Corp/Sponsorship". If it mentions EAD, H1B, or OPT, let it pass!
        3. NEVER REJECT FOR EXPERIENCE: Even if a job asks for 8, 10, or 15+ years of experience, YOU MUST SET `is_match = True`. Do NOT filter out senior roles. The candidate's CMU Master's prepares them for these.
        4. NEVER REJECT FOR SKILLS: Even if the candidate is completely missing required skills (e.g., Angular, Rust, AWS), YOU MUST SET `is_match = True`. Do NOT filter out jobs based on missing tech stack.
        5. GAP ANALYSIS: Use the 'missing_from_resume' field to highlight what the resume lacks (e.g., "Requires 8 years of experience and Angular"). This is where you note discrepancies—do NOT reject the job because of them. Keep it to 1-2 punchy sentences. Put 'None' if they are a perfect match.
        6. SCORING: If it passes rules #1 and #2, give it a high match_score (70-100), regardless of missing skills or experience gaps.
        
        JOB DESCRIPTION:
        {description}
        """

        try:
            # Using OpenAI's native structured outputs (beta.parse)
            completion = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=JobEvaluation,
                temperature=0.1
            )
            
            eval_result: JobEvaluation = completion.choices[0].message.parsed
            
            # Enrich job object
            job.parsed_salary = eval_result.salary_range
            job.parsed_experience = eval_result.experience_required
            job.parsed_skills = eval_result.tech_stack
            job.job_summary = eval_result.job_summary
            job.ai_rejection_reason = eval_result.rejection_reason
            job.missing_from_resume = eval_result.missing_from_resume
            
            if not eval_result.is_match:
                print(f"[AiFilter] ❌ Rejected: {job.title} @ {job.company} | Reason: {eval_result.rejection_reason}")
                return job, 0.0
                
            return job, float(eval_result.match_score)
            
        except Exception as e:
            print(f"[AiFilter] ⚠️ AI Evaluation failed for {job.title}: {e}")
            job.job_summary = "AI Error evaluating job."
            return job, 100.0

    def filter_jobs(self, jobs):
        """Processes a list of jobs concurrently and returns the matches."""
        import concurrent.futures
        
        matched_jobs = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_job = {executor.submit(self._evaluate_one, job): job for job in jobs}
            
            for future in concurrent.futures.as_completed(future_to_job):
                try:
                    job, score = future.result()
                    if score > 0:
                        matched_jobs.append(job)
                except Exception as exc:
                    print(f"[AiFilter] Error processing job list: {exc}")
                    
        return matched_jobs
