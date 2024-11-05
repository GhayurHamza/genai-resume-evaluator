from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.llm import LLMChain

load_dotenv()
 
class CustomAzureChatOpenAI(AzureChatOpenAI):
    def __init__(self, temperature: float):
        super().__init__(
            default_headers={"User-Id": os.getenv('USER_ID')},
            temperature=temperature,
            deployment_name=os.getenv('DEPLOYMENT_NAME'),
        )

    def resume_parser(self,resume_text):
        context = f"Resume text: {resume_text}"
        question = """ From above candidate's resume text, extract the only following details:
                    name: (Find the candidate's full name. If not available, specify "not available.")
                    email: (Locate the candidate's email address. If not available, specify "not available.")
                    nuber: (Identify the candidate's phone number. If not found, specify "not available.")
                    degree: A list of degrees obtained.
                    educational_institutions: A list of universities and colleges attended, cstart adding by adding latest..
                    total_exp: (If not explicitly mentioned, calculate the years of experience by analyzing the time durations at each company or position listed. Sum up the total durations to estimate the years of experience. If not determinable, write "not available.")
                    skills: Extract the skills which are purely technical and represent them as: [skill1, skill2,... <other skills from resume>]. If no skills are provided, state "not available."
                    designation: (Identify the candidate's job profile or designation,specific role or technology. If not mentioned, specify "not available.")
                    current_company: The latest company in the  professional work expirience 
                    summary: Create a concise summary including the candidate's name, highest educational detail with college/university name (if available), total years of professional experience, if professional experience is not there then add internship experience in months/years, specialization in specific expertise or technology, advanced skills, and significant contributions in their field.
                    """
        prompt = f"""
        Based on the below given candidate information, only answer asked question:
        Format the output in a JSON structure:
        {context}
        Question: {question}"""
        PROMPT = PromptTemplate(
            input_variables=["context", "question"], template=prompt
        )
        chain = LLMChain(llm=self, prompt=PROMPT, verbose=True)
        response = chain.run({"context": context, "question": question})
        return response
