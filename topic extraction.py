from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import text
import spacy
from names_dataset import NameDataset, NameWrapper
# Define your custom stop words
custom_stop_words = list(text.ENGLISH_STOP_WORDS.union(['al', 'Al','wa', 'Wa', 'fa', 'Fa', 'bi', 'Bi', 'fi', 'Fi', 'wa',
                                                        'Wa', 'la', 'La','ul','Ul','vv','bin','Bin','ibn','ought','surah',
                                                        'Surah','Ibn','ibnu','Ibnu','ibni','swt','Swt','pbuh','Pbuh','abu',
                                                        'prophet','Prophet','ahad','lamz','abtar','khair','arabia','sadr',]))
# Function to extract topics from a paragraph
def extract_topics(paragraph, num_topics):
    vectorizer = TfidfVectorizer(stop_words=custom_stop_words)
    tfidf_matrix = vectorizer.fit_transform([paragraph])
    feature_array = vectorizer.get_feature_names_out()
    tfidf_sorting = tfidf_matrix.toarray()[0].argsort()[::-1]

    top_n_keywords = []
    for i in range(num_topics):
        top_n_keywords.append(feature_array[tfidf_sorting[i]])

    return top_n_keywords

def extract_names(text):
    # Load English tokenizer, tagger, parser, NER and word vectors
    nlp = spacy.load("en_core_web_sm")

    # Process whole documents
    doc = nlp(text)

    nd = NameDataset()
    common_words = []
    # Analyze syntax
    names = [chunk.text for chunk in doc.ents if chunk.label_ == 'PERSON' and NameWrapper(nd.search(chunk.text.lower())).describe]

    # Convert list to set to remove duplicates and then convert it back to list
    names = list(set(names))

    return names



# Open the file
with open('tasfeer.txt', 'r',encoding='utf-8') as file:
    chapter_content = []
    chapter_number = None


    # Read the file line by line
    for line in file:
        # Check if the line starts a new chapter
        if line.startswith("Chapter"):
            # If we have content from a previous chapter, process it
            if chapter_content:
                print(f"Processing Chapter {chapter_number}...")
                print(extract_topics(" ".join(chapter_content), 20))
                print(extract_names(" ".join(chapter_content)))


            # Start a new chapter
            chapter_number = line.split()[1].strip(':')  # Get the chapter number
            chapter_content = []  # Reset the chapter content
        else:
            # This line is part of the current chapter, so add it to the content
            chapter_content.append(line.strip())

    # Don't forget to process the last chapter
    if chapter_content:
        print(f"Processing Chapter {chapter_number}...")
        print(extract_topics(" ".join(chapter_content), 20))
        print(extract_names(" ".join(chapter_content)))
