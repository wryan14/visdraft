import os
import shutil
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, LargeBinary
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from PIL import Image
import io

# Database setup
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
    description = Column(Text)
    translated = Column(Boolean, default=False)
    plain_text = Column(Text)
    plain_text_filename = Column(String(255))
    cover_image = Column(LargeBinary)
    cover_image_filename = Column(String(255))
    youtube_text = Column(Text)
    youtube_text_filename = Column(String(255))

def get_db_session():
    db_path = r'C:\Users\rdw71\Downloads\latin-repository\instance\patrologia_latina.db'
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    return Session()

def get_volume_data(title):
    session = get_db_session()
    volume = session.query(Volume).filter(Volume.english_title == title).first()
    session.close()
    
    if volume:
        return {
            'title': volume.english_title,
            'author': volume.author_english,
            'year': volume.year,
            'genre': volume.genre,
            'description': volume.description,
            'plain_text': volume.plain_text,
            'plain_text_filename': volume.plain_text_filename,
            'latin_title': volume.latin_title,
            'cover_image': volume.cover_image,
            'cover_image_filename': volume.cover_image_filename,
            'youtube_text': volume.youtube_text,
            'youtube_text_filename': volume.youtube_text_filename
        }
    return None

def process_volume(volume_key, volume):
    """Process a single volume from the database"""
    volume_data = get_volume_data(volume_key)
    if not volume_data:
        raise ValueError(f"Volume with title '{volume_key}' not found in the database.")

    # Setup directories
    backup_directory_base = "E:/BookScanner/Obscure Translations"
    directory_name = f"{volume_data['title']} - {volume_data['author']}"
    base_dir = os.path.join(backup_directory_base, directory_name)
    
    # Create directory structure
    directories = {
        'metadata': os.path.join(base_dir, "Metadata"),
        'ssml': os.path.join(base_dir, "SSML"),
        'audio': os.path.join(base_dir, "Audio"),
        'latin': os.path.join(base_dir, "Latin")
    }

    for dir_path in directories.values():
        os.makedirs(dir_path, exist_ok=True)

    # Process and save files
    _save_metadata(directories['metadata'], volume_data)
    _save_latin_text(directories['latin'], volume_data)
    _save_cover_image(directories['metadata'], volume_data)

    return {
        'status': 'success',
        'message': f'Volume processed successfully: {volume_key}',
        'output_directory': base_dir
    }

def _save_metadata(metadata_dir, volume_data):
    """Save metadata to a text file"""
    metadata_path = os.path.join(metadata_dir, "metadata.txt")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(f"Title: {volume_data['title']}\n")
        f.write(f"Author: {volume_data['author']}\n")
        f.write(f"Year: {volume_data['year']}\n")
        f.write(f"Genre: {volume_data['genre']}\n")
        f.write(f"Description: {volume_data['description']}\n")

def _save_latin_text(latin_dir, volume_data):
    """Save Latin text to file"""
    if volume_data['plain_text'] and volume_data['plain_text_filename']:
        latin_path = os.path.join(latin_dir, volume_data['plain_text_filename'])
        text = volume_data['plain_text']
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        with open(latin_path, 'w', encoding='utf-8') as f:
            f.write(text)

def _save_cover_image(metadata_dir, volume_data):
    """Save cover image"""
    if volume_data['cover_image']:
        cover_path = os.path.join(metadata_dir, "Cover_Image.png")
        image = Image.open(io.BytesIO(volume_data['cover_image']))
        image.save(cover_path, format='PNG')