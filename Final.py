import cv2
import pytesseract
import re
import json
from PIL import Image

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binarized = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    return binarized

def extract_text_from_image(image, lang_code='guj+eng'):
    pil_image = Image.fromarray(image)
    extracted_text = pytesseract.image_to_string(pil_image, lang=lang_code)
    return extracted_text

import re
import json

def parse_jantri_data(text):
    header_pattern = re.compile(
        r'જીલ્લો:\s*([A-Z]+)\s+તાલુકા\s*\?([A-Z]+)\s*\d+\s*'
        r'વિસ્તાર નામ\s*:\s*([A-Z\s]+)',
        re.DOTALL
    )
    header_match = header_pattern.search(text)
    
    if not header_match:
        return []

    district = header_match.group(1)
    taluka = header_match.group(2)
    area_name = header_match.group(3).strip()
    
    jantri_pattern = re.compile(
        r'(\d{2}/\d/\d(?:/[A-Z])?)\s+'
        r'(\d+)\s+'
        r'(\d+)\s+'
        r'(\d+)\s+'
        r'(\d+)\s+'
        r'(\d+)\s+'
        r'(\d+)\s+'
        r'\|?\s*(\d+)\s+'
        r'Block\. No\s*([\s\S]*?)(?=\n\n\d{2}/\d/\d|$)',
        re.MULTILINE
    )

    jantri_zones = []
    
    for match in jantri_pattern.finditer(text):
        zone_name = match.group(1)
        prices = [int(p) for p in match.groups()[1:8]]
        blocks_text = match.group(9)
        
        blocks_list = [
            block.strip()
            for block in blocks_text.replace('\n', ' ').replace(' ', '').split(',')
            if block.strip()
        ]
        
        jantri_zones.append({
            "જિલ્લો": district,
            "તાલુકા": taluka,
            "વિસ્તાર નામ": area_name,
            "ભાવ": {
                zone_name: {
                    "રહેણાંક ફ્લેટ/એપાર્ટમેન્ટ": prices[0],
                    "ઓફિસ": prices[1],
                    "દુકાન": prices[2],
                    "ઔદ્યોગિક": prices[3],
                    "ખુલ્લા પ્લોટનો ભાવ": prices[4],
                    "ખેતીની જમીનનો ભાવ (પીયત)": prices[5],
                    "ખેતીની જમીનનો ભાવ (બિન પીયત)": prices[6]
                }
            },
            "Block. No": blocks_list
        })
        
    return jantri_zones
    
if __name__ == "__main__":
    image_file = 'V.jpg'
    preprocessed_img = preprocess_image(image_file)
    text_content = extract_text_from_image(preprocessed_img, lang_code='guj+eng') 
    print(text_content)
    jantri_data = parse_jantri_data(text_content)
    print(json.dumps(jantri_data, indent=2, ensure_ascii=False)) 


