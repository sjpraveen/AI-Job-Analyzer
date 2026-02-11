import os
import streamlit as st
from src.core.agents import ResumeAnalysisAgent
from src.ui.ui import JobAnalyserUI

st.set_page_config(
    page_title="Job Analyse",
    layout="wide"
)


class JobAnalyzerApp:
    
    def __init__(self):
        self.ui = JobAnalyserUI()
        self.agent = ResumeAnalysisAgent()
        
    def run(self):
        self.ui.header()
        
        api_key = self.ui.sidebar()
        if not api_key:
            st.warning("Enter open AI API key ........")
            st.stop()
        os.environ['OPENAI_API_KEY'] = api_key
        
        resume = self.ui.upload_resume()
        jd = self.ui.upload_jd()
        

        
        if st.button("Analyze Resume and JD"):
            if not resume or not jd:
                st.error("Upload both resume and jd")
                
            with st.spinner("Analyzing Resume ..........."):
                results = self.agent.analyse(resume, jd)
                self.ui.show_results(results)


if __name__=="__main__":
    JobAnalyzerApp().run()        