import json
import re
from typing import List,Dict
from concurrent.futures import ThreadPoolExecutor

from pypdf import PdfReader
from langchain_openai import ChatOpenAI

from src.common.logger import get_logger
from src.common.custom_exception import CustomException

class ResumeAnalysisAgent:
    def __init__(self, cutoff_score:int = 75):
        self.logger = get_logger(__name__)
        self.cutoff_score = cutoff_score
        self.resume_text =""
        self.jd_text=""
        
        self.extracted_skills:List[str] = []
        
        self.logger.info("Resume Analisis Agent iniutialized ...")
        
    def _read_pdf(self,file) -> str:
        try:
            self.logger.info("Reading text from pdf file ...")
            reader = PdfReader(file)
            
            text = "\n".join(
                page.extract_text() or ""for  page in reader.pages
            )
            
            self.logger.info("pdf read success")
            
            return text
        except Exception as e:
            self.logger.error("Failed to read pdf file", exc_info=True)
            raise CustomException("Failed to read padf file", e)
    
    def _read_txt(self,file) -> str:
        try:
            self.logger.info("Reading TXT file...")
            text = (
                file.getvalue().decode("utf-8")
                if hasattr(file, "getvalue")
                else file.read().decode("utf-8")                    
            )
            
            self.logger.info("successully read TXT file")
            
            return text
        except Exception as e:
            self.logger.error("unable to read TXT file", exc_info=True)
            raise CustomException("failed to read TXT file")
        
    def extract_text(self,file) -> str:
        try:
            self.logger.info(f"Extracting content form the file") 
            
            ext = file.name.split(".")[-1].lower()
            
            if ext=="pdf":
                return self._read_pdf(file)
            if ext=="txt":
                return self._read_txt(file)
            else:
                self.logger.warning("unsupported file extension....")
                return ""
        except Exception as e:
            self.logger.error("Extraction failed", exc_info=True)   
            raise CustomException("Extraction Failed") 
        
    
    def extract_skills_from_jd(self,jd_text:str) -> List[str]:
        try:
            self.logger.info("extracting skills from jd")
            
            llm = ChatOpenAI(model="gpt-4.1-mini" , temperature=0)
            
            prompt = """
                Extract only technical skills from the given job decription.
                
                Rules:
                1. Return only in valid json format
                2. No markdown
                3. No explanation
                
                Example:
                ["python", "Docker", "AWS"]
              """
            response = llm.invoke(prompt+"\n\n"+jd_text)  
            
            skills = json.loads(response.content)
            
            
            if isinstance(skills, list):
                self.logger.info(f"Extracted skills from jd {skills}")
                return skills
            else:
                self.logger.warning("llm returned response is not valid")
                return []
        except Exception as e:
            self.logger.error("Extraction failed from jd", exc_info=True)   
            raise CustomException("Extraction Failed from jd")
    def _parse_markdown_json(self, raw_str):
        
        cleaned = raw_str.strip("'\"")
        
        cleaned = re.sub(r'```(?:json|python)?\s*|\s*```', '', cleaned, flags=re.IGNORECASE)
        
        return cleaned    
        
    def _evaluvate_skill(self,skill:str) -> Dict:
        try:
            self.logger.info(f"Evaluvating the skill= {skill}")
            
            llm = ChatOpenAI(model="gpt-4.1-mini" , temperature=0)
            
            prompt = f"""
            Evaluvate how clearly the resume shows proficiency in "{skill}
            Resume:
            {self.resume_text[:2500]}
            
            Return only with valid json format
            {{"skill":"{skill}", "score":0-10}}
            """
            
            response = llm.invoke(prompt)
            
            self.logger.info(f'response for the skill = {skill} is {response}') 
            
            result = json.loads(self._parse_markdown_json(response.content))
            
            return result
        except Exception as e:
            self.logger.error("Evaluvation of skill failed", exc_info=True)
            return {"skill": skill , "score":0}
    
    def evaluvate_skills(self) -> Dict:
        try:
            self.logger.info(f"Evaluvatiing skills ....")
            
            with ThreadPoolExecutor(max_workers=3)  as executor:
                results = list(
                    executor.map(self._evaluvate_skill, self.extracted_skills)
                )
            
            self.logger.info(f'results : {results}')    
                
            scores = {r["skill"] : r["score"] for r in results}
            
            strengths = [k for k , v in scores.items() if v>=7]
            
            missing = [k for k , v in scores.items() if v<=5]
            
            total_score = (
                int((sum(scores.values())/ (10*len(scores)))*100)
                if scores
                else 0
            )
            
            self.logger.info("Evaluvation of skills successfully completed...")
            return {
                "overall_score" : total_score,
                "selected": total_score>= self.cutoff_score,
                "skill_scores": scores,
                "strengths" : strengths,
                "missing" : missing
            }
            
        except Exception as e:
            self.logger.error("Evaluvation of skills failed")
            raise CustomException("Evaluvation of skills failed")
        
    def analyse(self,resume_file, jd_file) -> Dict:
        try:
            self.logger.info("Analysis started ......")
            self.resume_text = self.extract_text(resume_file)
            self.jd_text = self.extract_text(jd_file)
            
            self.extracted_skills = self.extract_skills_from_jd(self.jd_text)
            
            result = self.evaluvate_skills()
            
            return result
        except Exception as e:
            self.logger.error("Evaluvation failed", stack_info=True)
            raise CustomException("Evaluvation failed")
        
            
            
                 
            
        
            
            


