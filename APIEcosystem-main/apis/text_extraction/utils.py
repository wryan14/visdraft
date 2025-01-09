import os
import re
import time
import pandas as pd
import openai
from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, LargeBinary, DateTime, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def search_church_father(name):
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {'action': 'query', 'list': 'search', 'srsearch': name, 'format': 'json'}
    response = requests.get(search_url, params=params)

    if response.status_code == 200:
        search_results = response.json().get('query', {}).get('search', [])
        if not search_results:
            return "No results found."

        page_title = search_results[0]['title']
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"
        summary_response = requests.get(summary_url)

        if summary_response.status_code == 200:
            summary_data = summary_response.json()
            return summary_data.get('extract', 'No description available.')
        else:
            return f"Error: Unable to fetch summary (Status Code: {summary_response.status_code})"
    return f"Error: Unable to perform search (Status Code: {response.status_code})"


def process_html(volume, first_relevant_title, last_relevant_title, database_title, add_author, author_description):

    # Database setup
    db_path = r'C:\Users\rdw71\Downloads\latin-repository\instance\patrologia_latina.db'
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    Base = declarative_base()

    class Volume(Base):
        __tablename__ = 'volume'

        id = Column(Integer, primary_key=True)
        volume = Column(Integer, nullable=False)
        author = Column(String(200), nullable=False)
        author_english = Column(String(200))
        latin_title = Column(Text, nullable=False)
        english_title = Column(Text)
        year = Column(String(50))
        genre = Column(String(200))
        page = Column(String(50))
        plain_text = Column(Text)
        plain_text_filename = Column(String(255))
        youtube_text = Column(Text)
        youtube_text_filename = Column(String(255))
        notes = Column(Text)
        description = Column(Text)
        translated = Column(Boolean, default=False)
        cover_image = Column(LargeBinary)
        cover_image_filename = Column(String(255))
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    # Retrieve the API key from the environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("API key for OpenAI is not set. Please set the OPENAI_API_KEY environment variable.")

    # Function to send requests to OpenAI
    def gpt_send(prompt_text):
        for attempt in range(5):  # Retry up to 5 times
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt_text}],
                    max_tokens=2048,
                    temperature=0.7
                )
                if response.choices and response.choices[0].message:
                    return response.choices[0].message.content.strip()
                else:
                    print(f"No response generated. Attempt: {attempt + 1}, Response: {response}")
                    time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                print(f"Exception occurred: {e}. Attempt: {attempt + 1}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Failed to process text after multiple attempts")

    # Function to extract a sample from the text
    def extract_sample(text, sample_length=500):
        return text[:sample_length]

    # Function to generate metadata
    def generate_metadata(title, sample_text, collection_name=None):
        prompt_text = (
            f"Create metadata for the following text sample in the specified format and translate both the title and the content into English:\n\n"
            f"Title: {title}\n"
            f"Sample: {sample_text}\n\n"
            f"The metadata should include: title, author, year, genre, and a detailed description. "
        )
        
        if collection_name:
            prompt_text += f"\nThis document is part of a collection called '{collection_name}'."
        
        prompt_text += (
            f"\nThe response should be formatted as follows:\n"
            f"title = \"<title>\"\n"
            f"author = \"<author>\"\n"
            f"year = \"<year>\"\n"
            f"genre = \"<genre>\"\n"
            f"description = (\n"
            f"\"\"\"<description>\"\"\"\n"
            f")\n"
            f"Ensure the description is concise, approximately 100-150 words."
        )
        
        return gpt_send(prompt_text)

    # Load the HTML file
    with open(f'E:/Translation/Patrologia_Latina/Patrologia_Latina_Vol_{volume}_Cleaned.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Function to extract content between start and end titles
    def extract_content(content, start_title, end_title):
        start_index = content.index(start_title)
        end_index = content.index(end_title, start_index) + len(end_title)
        return content[start_index:end_index]

    # Extract the relevant content
    relevant_content = extract_content(html_content, first_relevant_title, last_relevant_title)



    # Function to split content into chapters
    def split_into_chapters(content):
        # This regex looks for <h4> or <center> tags, which likely denote chapter titles
        chapter_splits = re.split(r'(<h4.*?</h4>|<center.*?</center>)', content, flags=re.DOTALL)
        
        chapters = []
        current_title = ""
        current_content = ""
        
        for split in chapter_splits:
            if re.match(r'<h4|<center', split.strip()):
                if current_title and current_content:
                    chapters.append((current_title, current_content))
                current_title = split.strip()
                current_content = split  # Include the header in the content
            else:
                current_content += split

        if current_title and current_content:
            chapters.append((current_title, current_content))
        
        return chapters

    # Split the content into chapters
    chapters = split_into_chapters(relevant_content)


    # Create DataFrames
    df_text = pd.DataFrame(chapters, columns=['Title', 'Text'])
    df_html = pd.DataFrame(chapters, columns=['Title', 'HTML'])

    # Clean up the text content by removing HTML tags, but keep the text of the headers
    df_text['Text'] = df_text['Text'].apply(lambda x: re.sub(r'<.*?>', '', x).strip())

    # Extract plain text titles
    df_text['Title'] = df_text['Title'].apply(lambda x: re.sub(r'<.*?>', '', x).strip())
    df_html['Title'] = df_html['Title'].apply(lambda x: re.sub(r'<.*?>', '', x).strip())


    # Create filtered DataFrames
    filtered_df_text = df_text.copy()
    filtered_df_html = df_html.copy()

    # Remove the first and last entries if they match the relevant titles
    filtered_df_text = filtered_df_text[~filtered_df_text['Title'].isin([first_relevant_title, last_relevant_title])].reset_index(drop=True)
    filtered_df_html = filtered_df_html[~filtered_df_html['Title'].isin([first_relevant_title, last_relevant_title])].reset_index(drop=True)

    # Combine the text and HTML output into single strings
    combined_text = ' '.join(filtered_df_text['Text'].tolist())
    combined_html = ' '.join(filtered_df_html['HTML'].tolist())

    # Remove specific characters
    combined_text = combined_text.replace('»','').replace('«','')
    combined_html = combined_html.replace('»','').replace('«','')

    combined_html = combined_html.replace(first_relevant_title, '').replace(last_relevant_title, '')
    combined_html = combined_html.strip('<h4><center>')

    print("COMBINED HTML")
    print(combined_html[0:100])
    
    # Clean up the start title to create a valid filename
    def clean_title_for_filename(title):
        return re.sub(r'\W+', '_', title)

    cleaned_title = clean_title_for_filename(database_title)

    # Create directory for the volume
    os.makedirs(f'Volume_{volume}', exist_ok=True)

    # Save the combined text to a text file
    with open(f'Volume_{volume}/{cleaned_title}.txt', 'w', encoding='utf-8') as output_file:
        output_file.write(combined_text)

    # Save the combined HTML to a text file
    with open(f'Volume_{volume}/{cleaned_title[:60]}_html.txt', 'w', encoding='utf-8') as output_file:
        output_file.write(combined_html)

    print(f'Text saved to Volume_{volume}/{cleaned_title}.txt')
    print(f'HTML saved to Volume_{volume}/{cleaned_title}_html.txt')

    # Calculate the sample length for each title
    total_tokens = 2048 - 500  # reserve some tokens for metadata
    num_titles = len(filtered_df_text)
    sample_length = total_tokens // num_titles

    # Extract samples and gather them
    title_samples = []
    for title, text in filtered_df_text.itertuples(index=False):
        sample_text = extract_sample(text, sample_length)
        title_samples.append((title, sample_text))

    # Generate metadata for each title and add it to the DataFrame
    metadata_list = []
    for title, sample_text in title_samples:
        metadata = generate_metadata(title, sample_text, collection_name=database_title)
        metadata_list.append(metadata)

    filtered_df_text['Metadata'] = metadata_list

    # Save the DataFrame to a CSV file
    filtered_df_text.to_csv(f'Volume_{volume}/filtered_texts_with_metadata.csv', index=False)

    # Display the DataFrame with metadata
    print(filtered_df_text)

    # Function to generate overarching metadata
    def generate_overarching_metadata(metadata_list, add_author=None, author_description=None):
        combined_metadata = "\n\n".join(metadata_list)
        if add_author:
            prompt_text = (
            f"Create an overarching metadata record for the following individual metadata entries, combining them into a comprehensive record:\n\n"
            f"{combined_metadata}\n\n"
            f"The overarching metadata should include: title, author, year, genre, and a detailed description. "
            f"The response should be formatted as follows:\n"
            f"title = \"<title>\"\n"
            f"author = \"{add_author}\"\n"
            f"year = \"<year>\"\n"
            f"genre = \"<genre>\"\n"
            f"description = (\n"
            f"\"\"\"<description>\"\"\"\n"
            f")\nShort Author Description - {author_description}"
            f"Ensure the description is concise, approximately 100-150 words."
                
        )
        else:
            prompt_text = (
                f"Create an overarching metadata record for the following individual metadata entries, combining them into a comprehensive record:\n\n"
                f"{combined_metadata}\n\n"
                f"The overarching metadata should include: title, author, year, genre, and a detailed description. "
                f"The response should be formatted as follows:\n"
                f"title = \"<title>\"\n"
                f"author = \"<author>\"\n"
                f"year = \"<year>\"\n"
                f"genre = \"<genre>\"\n"
                f"description = (\n"
                f"\"\"\"<description>\"\"\"\n"
                f")\n"
                f"Ensure the description is concise, approximately 100-150 words."
            )
        return gpt_send(prompt_text)

    def generate_youtube_description(overarching_metadata, filtered_df_text, database_title, add_author, combined_text):
        # Extract individual chapter metadata
        chapter_metadata = filtered_df_text['Metadata'].tolist()
        
        # Extract a sample of the full text
        text_sample = combined_text[:5000]  # Adjust this number as needed
        
        prompt_text = (
            f"Based on the following information, create an engaging YouTube description and title for a video about this work:\n\n"
            f"Overarching Metadata:\n{overarching_metadata}\n\n"
            f"Individual Chapter Metadata:\n{' '.join(chapter_metadata)}\n\n"
            f"Text Sample:\n{text_sample}\n\n"
            f"The YouTube description should include:\n"
            f"1. A brief neutral-academic introduction of \"{database_title}\" by {add_author}\n"
            f"2. The context or time period of the work\n"
            f"3. 4-5 key features or main points of the work, drawing from the chapter metadata and text sample\n"
            f"4. The work's significance or relevance, both in its original context and potentially for modern readers\n"
            f"5. 5-7 relevant hashtags\n\n"
            f"For the YouTube title, create an accurate title based on the title of the work and the author "
            f"The response should be formatted as follows:\n"
            f"youtube_description = \"\"\"\n"
            f"[YouTube description here]\n"
            f"\"\"\"\n"
            f"youtube_title = \"[YouTube title here]\"\n"
            f"Ensure the description is informative, engaging, and reflects a comprehensive understanding of the text. "
            f"The title should be accurate but can be expanded to be attention-grabbing and make viewers want to learn more about the work."
        )
        
        return gpt_send(prompt_text)

    # Generate and display the overarching metadata
    overarching_metadata = generate_overarching_metadata(metadata_list, add_author=add_author, author_description=author_description)
    print("Overarching Metadata:")
    print(overarching_metadata)

    youtube_content = generate_youtube_description(overarching_metadata, filtered_df_text, database_title, add_author, combined_text)
    print("YouTube Content:")
    print(youtube_content)

    with open(f'Volume_{volume}/{cleaned_title}_youtube_content.txt', 'w', encoding='utf-8') as youtube_file:
        youtube_file.write(youtube_content)

    # Save the overarching metadata to a text file
    with open(f'Volume_{volume}/{cleaned_title}_overarching_metadata.txt', 'w', encoding='utf-8') as meta_file:
        meta_file.write(overarching_metadata)

    print(f'Overarching metadata saved to Volume_{volume}/{cleaned_title}_overarching_metadata.txt')


    import json

    def generate_custom_image_prompt(template, metadata):
        
        
        prompt = f"""
    Please provide a detailed image prompt based on the following book metadata:

    {metadata}

    Use the following template as inspiration for the style and structure of the image, but feel free to adapt and customize it based on the book's content and themes:

    {template}

    Important constraints to maintain:
    1. The image should be square with dimensions of 1024x1024 pixels.
    2. Maintain the overall style of an illuminated manuscript from the book's time period.
    3. Include an ornate frame with a central space for the book's title.
    4. Use a color scheme of gold, deep red, royal blue, and ivory white on a warm, aged parchment background.
    5. Do not depict any human figures or faces.

    Provide a detailed, cohesive image prompt combining elements from the template and the book's unique characteristics. Start directly with the image description.
    """
        
        return gpt_send(prompt)

    # Example usage
    template = """Create a square image with dimensions of 1024x1024 pixels, in the style of a 4th-century illuminated manuscript. Design an ornate frame that occupies most of the image, leaving a thin border of aged parchment visible. Include:
    * Elaborate golden scrollwork and filigree patterns forming the main structure of the frame
    * A central rectangular space left empty for later text insertion, occupying about 1/3 of the image's width and height
    * In the top center, depict a stylized cross or Chi-Rho symbol (☧)
    * In the four corners, include symbolic elements representing:
    * Top left: A bishop's mitre or crosier (representing Lucifer of Cagliari)
    * Top right: An imperial crown or scepter (symbolizing Emperor Constantius)
    * Bottom left: Tablets of stone (representing the law of God)
    * Bottom right: A quill or scroll (symbolizing religious treatises)
    * Subtly integrate elements that suggest conflict or steadfastness, such as:
    * A simplified sword or shield
    * Chains or broken chains
    * A flame symbolizing unwavering faith
    * Use a color scheme of gold, deep red, royal blue, and ivory white on a warm, aged parchment background
    * Include delicate vine or acanthus leaf motifs extending from the scrollwork
    The overall design should evoke the gravity of a 4th-century religious treatise, with elements suggesting conflict between church and state, unwavering faith, and the defense of Catholic doctrine against Arianism. The style should reflect the artistic capabilities of the era, focusing on symbolic representation rather than realism."""


    custom_prompt = generate_custom_image_prompt(template, overarching_metadata)

    my_image = openai.images.generate( model="dall-e-3",
    prompt=custom_prompt,
    size="1024x1024",
    quality="standard",
    n=1,)

    # Extract the image URL from the response
    image_url = my_image.data[0].url


    # Truncate cleaned_name to the first 60 characters
    file_name = cleaned_title[:60]

    # Ensure the file name is valid by replacing or removing invalid characters
    file_name = "".join(x if x.isalnum() or x in " ._-" else "_" for x in file_name)

    # Append the file extension
    file_name += ".png"

    # Fetch the image using the image URL
    response = requests.get(image_url)

    # Save the image to a file
    with open(file_name, 'wb') as file:
        file.write(response.content)

    print(f"Image saved as {file_name}")

    # After generating the overarching metadata and image

    # Function to create a clean, database-friendly filename
    def create_db_friendly_filename(title, volume):
        clean_title = clean_title_for_filename(title)
        return f"Volume_{volume}_{clean_title}"

    session = Session()

    def parse_metadata(metadata_string):
        metadata_dict = {}
        lines = metadata_string.split('\n')
        current_key = None
        current_value = []
        
        for line in lines:
            if '=' in line and not current_key:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"')
                
                if value.startswith('('):
                    current_key = key
                    current_value = [value[1:]]  # Remove the opening parenthesis
                else:
                    metadata_dict[key] = value
            elif current_key:
                if line.strip().endswith(')'):
                    current_value.append(line.strip()[:-1])  # Remove the closing parenthesis
                    metadata_dict[current_key] = '\n'.join(current_value).strip().strip('"""')
                    current_key = None
                    current_value = []
                else:
                    current_value.append(line.strip())
        
        return metadata_dict

    # Parse the overarching metadata
    metadata_dict = parse_metadata(overarching_metadata)

    # Create database-friendly filenames
    db_friendly_filename = create_db_friendly_filename(database_title, volume)
    plain_text_filename = f"{db_friendly_filename}.txt"
    html_filename = f"{db_friendly_filename}_html.txt"

    # Check if the volume exists in the database
    volume_entry = session.query(Volume).filter_by(volume=volume, latin_title=database_title).first()

    if volume_entry:
        # Update the existing entry
        volume_entry.genre = metadata_dict.get('genre', '')
        volume_entry.description = metadata_dict.get('description', '')
        volume_entry.year = metadata_dict.get('year', '')
        
        # Update plain text filename
        volume_entry.plain_text_filename = plain_text_filename
        
        # Update plain text content
        with open(f'Volume_{volume}/{cleaned_title[:60]}_html.txt', 'r', encoding='utf-8') as f:
            volume_entry.plain_text = f.read()
        
        # Update cover image
        with open(file_name, 'rb') as image_file:
            volume_entry.cover_image = image_file.read()
        volume_entry.cover_image_filename = create_db_friendly_filename(file_name, volume)
        volume_entry.notes = "A - Text and Image"
        session.commit()
        print(f"Updated database entry for Volume {volume}, Title: {database_title}")
    else:
        print(f"No matching entry found for Volume {volume}, Title: {database_title}")

    session.close()
    print("Processing complete.")


    def save_youtube_to_db(volume, title, youtube_content):
        session = Session()
        try:
            volume_entry = session.query(Volume).filter_by(volume=volume, latin_title=title).first()
            if volume_entry:
                volume_entry.youtube_text = youtube_content
                volume_entry.youtube_text_filename = f"Volume_{volume}_youtube.txt"
                session.commit()
                print(f"YouTube content saved to database for Volume {volume}, Title: {title}")
            else:
                print(f"No matching entry found for Volume {volume}, Title: {title}")
        except Exception as e:
            print(f"Error saving YouTube content to database: {e}")
            session.rollback()
        finally:
            session.close()

    # Usage
    save_youtube_to_db(volume, database_title, youtube_content)

    return combined_html