import pandas as pd
import ollama


# Function to get LLM response from the provided model
def get_ollama(prompt):
    response = ollama.generate(model='gemma2', prompt=prompt)
    return response['response']

def get_excluded(title, abstract) :
    prompt = f"""
    Read the following research article and answer:
    Title: {title}\nAbstract: {abstract}\n
    1) if it is a review / editorial / anything other than a research article, say 'other article types'
    2) if the topic is focused on rehabilitation , say 'rehabilitation'
    3) if this article is describing an experience about a commercial product or a model developed outside of the research group, say 'experience'
    4) if the topic is on hemorrhage, say 'hemorrhage'
    5) if the research is not concerning human subjects, say 'non-human'
    6) if the article language is not in english say 'language'
    7) if the article is about a study protocol, say 'protocol'
    8) if the article is NOT related to stroke, say 'not related'
    9) if none of these apply, say 'none'
     just give me the answer without any description of other introduction, do not say 'stroke' or 'research'
    """
    return get_ollama(prompt)

def get_category(title, abstract) :
    prompt = f"""
    Read the following research article and answer:
    Title: {title}\nAbstract: {abstract}\n
    1) Risk: if it is about stroke risk occurrence prediction, say 'risk'
    2) Diagnosis: if it is about diagnosis of stroke it would be 'diagnosis', for example like presence of LVO on angiography or imaging analysis such as NCCT or MRI aanalysis, segmentation, or mismathc calculation, hemorrhage detection, time-of-onset prediction, triage, and may be treatment decision support. say 'diagnosis'
    3) Prediction of etiology: thrombus or clot analysis to predict or classify the etiology. or imaging analysis or any other prediction including clinical variable that aims to predict the etiology (TOAST classification) of the stroke. say 'etiology'
    4) Prognosis: all articles related to stroke prognosis or outcomes. mRS, hemorrhagic transformation, reperfusion success, END, stroke recurrence, progression, hospital stay, bedroom stay time? QoL subtypes, readmission, discharge disposition, fall prediction, mental outcome, cognitive, depressive outcome. say 'prognosis'
    5) Comorbidities: suc as CAD prediction or DVT, seizure, cognitive , pneumonia or etc. prediction of comorbidities, say 'comorbidities'
    6) Other : all other types such as transporation related, imaging reconstruction or enhancement, difficult femoral access prediction. say 'other'
     just give me the answer without any description of other introduction and only one category that best matches should be said
    """
    return get_ollama(prompt)


# Function to categorize articles and fill the required columns
def categorize_articles(file_path):
    # Read the xlsx file into a pandas DataFrame
    df = pd.read_excel(file_path)

    # Add new columns for categorization
    df['excluded'] = ''
    df['category'] = ''
    
    # Iterate over each row and apply the LLM-based categorization logic
    for index, row in df.iterrows():
        title = row['Title']
        abstract = row['Abstract']
        
        excluded= get_excluded(title, abstract)
        df.at[index, 'excluded'] = excluded.strip()
        if ('none' in excluded.lower()) | ('stroke' in excluded.lower()) :
            category= get_category(title, abstract)
            df.at[index, 'category'] = category.strip()


    # Save the modified DataFrame back to a new xlsx file
    output_file = file_path.replace('.xlsx', '_categorized.xlsx')
    df.to_excel(output_file, index=False)
    
    return output_file

# Example usage
file_path = "pubmed_results.xlsx"  # Replace with actual file path
output_file = categorize_articles(file_path)
print(f"Categorized file saved to: {output_file}")