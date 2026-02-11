from streamlit import streamlit as st

class JobAnalyserUI:
    
    def header(self):
        st.title("Evaluvate Job  Analyzer")
        st.caption("Resume vs JD analyzer")
        st.divider()
        
    def sidebar(self):
        with st.sidebar:
            st.header("API key Configuration")
            return st.text_input("Open AI API key here", type="password")
        
    def upload_resume(self):
        st.subheader("Upload Resume")
        return st.file_uploader("Upload resumer here", type=["pdf"])
    
    def upload_jd(self):
        st.subheader("Upload JD")
        return st.file_uploader("Upload JD here", type=["pdf"])
    
    def show_results(self, result:dict):
        st.divider()
        st.subheader("Analysis Report")
        
        st.write(f'### Score: {result["overall_score"]}/100')
        
        if result["selected"]:
            st.success("Candidate is shortlisted")
        else:
            st.error("Candidate  rejected")
            
        st.subheader("Strengths")    
        if result["strengths"]:
            for s in result["strengths"]:
                st.write(f"-{s}  ({result["skill_scores"][s]}/10)")
        else:
            st.write("No strong skills in the resume")
        
        
        st.subheader("Areas of Improvement")    
        if result["missing"]:
            for s in result["missing"]:
                st.write(f"-{s}  ({result["skill_scores"][s]}/10)")
        else:
            st.write("No major skill gap found")              
                
                
        