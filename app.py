import streamlit as st
from prompts import build_prompt, build_image_prompt
from utils import call_ai_model, call_vision_model, call_vision_model_multi, process_html_result
import base64
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="Counterfeit Risk Checker", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .risk-low {
        color: #28a745;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
        background-color: rgba(40, 167, 69, 0.1);
    }
    .risk-medium {
        color: #ffc107;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
        background-color: rgba(255, 193, 7, 0.1);
    }
    .risk-high {
        color: #dc3545;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
        background-color: rgba(220, 53, 69, 0.1);
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
    .flag-red {
        color: #dc3545;
        padding: 3px 8px;
        border-radius: 3px;
        background-color: rgba(220, 53, 69, 0.1);
        margin-bottom: 5px;
        display: inline-block;
    }
    .flag-green {
        color: #28a745;
        padding: 3px 8px;
        border-radius: 3px;
        background-color: rgba(40, 167, 69, 0.1);
        margin-bottom: 5px;
        display: inline-block;
    }
    .condition-header {
        font-weight: 600;
        margin-top: 1rem;
        color: #6c757d;
    }
    .condition-rating {
        font-weight: bold;
    }
    .condition-notes {
        font-style: italic;
        color: #6c757d;
    }
    .age-header {
        font-weight: 600;
        margin-top: 1rem;
        color: #6c757d;
    }
    .age-assessment {
        font-style: italic;
        color: #6c757d;
    }
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .explanation {
        font-style: italic;
        margin: 1rem 0;
    }
    .tips-header, .visual-header, .flags-header {
        font-weight: 600;
        margin-top: 1rem;
    }
    .platform-header {
        font-weight: 600;
        margin-top: 1rem;
    }
    .tab-content {
        padding: 10px 0;
    }
    .disclaimer {
        font-size: 0.8rem;
        color: #6c757d;
        font-style: italic;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>Counterfeit Risk Checker</h1>", unsafe_allow_html=True)
st.markdown("Evaluate the risk of counterfeit luxury items before buying")

# Create tabs for different analysis methods
tab1, tab2 = st.tabs(["Basic Check", "Visual Authentication"])

# Tab 1: Basic Check (Form-based)
with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown("Enter the item details to get a basic counterfeit risk assessment.")
    
    with st.form("risk_checker_form"):
        # Predefined list of luxury brands
        brand_options = [
            "",
            # Luxury Fashion
            "Louis Vuitton",
            "Chanel",
            "Dior",
            "Gucci",
            "Hermès",
            "Prada",
            "Balenciaga",
            "Fendi",
            "Saint Laurent",
            "Bottega Veneta",
            "Burberry",
            "Celine",
            "Valentino",
            "Loewe",
            "Givenchy",
            "Versace",
            "Miu Miu",
            "Alexander McQueen",
            "Jacquemus",
            "The Row",
            # Watches & Jewelry
            "Rolex",
            "Cartier",
            "Patek Philippe",
            "Audemars Piguet",
            "Omega",
            "Tiffany & Co.",
            "Van Cleef & Arpels",
            "Bulgari",
            # Streetwear & Contemporary
            "Supreme",
            "Off-White",
            "Bape",
            "Stone Island",
            "Chrome Hearts",
            "Palm Angels",
            "Fear of God",
            "Amiri",
            "Kith",
            "Stüssy",
            "Aimé Leon Dore",
            # Other
            "Other"
        ]
        
        # Item types
        item_options = [
            "",
            # Bags & Accessories
            "Handbag",
            "Tote",
            "Crossbody Bag",
            "Backpack",
            "Clutch",
            "Wallet",
            "Card Holder",
            "Belt",
            "Sunglasses",
            "Scarf",
            # Apparel
            "T-Shirt",
            "Hoodie",
            "Sweater/Knitwear",
            "Jacket/Coat",
            "Denim/Jeans",
            "Dress", 
            "Skirt",
            "Pants/Trousers",
            "Button-Up Shirt",
            "Polo Shirt",
            # Footwear
            "Sneakers",
            "Dress Shoes",
            "Heels",
            "Boots",
            "Sandals",
            # Luxury Items
            "Watch",
            "Bracelet",
            "Necklace",
            "Earrings",
            "Ring",
            # Other
            "Other"
        ]
        
        # Platform options
        platform_options = [
            "",
            "eBay",
            "The RealReal",
            "Vestiaire Collective",
            "Poshmark",
            "Grailed",
            "Depop",
            "StockX",
            "Facebook Marketplace",
            "Local Consignment",
            "Other"
        ]
        
        # Form inputs
        selected_brand = st.selectbox("Select Brand", brand_options)
        
        # If "Other" is selected, show text input
        if selected_brand == "Other":
            brand = st.text_input("Enter Brand Name")
        else:
            brand = selected_brand
        
        selected_item = st.selectbox("Select Item Type", item_options)
        
        # If "Other" is selected, show text input
        if selected_item == "Other":
            item_type = st.text_input("Enter Item Type")
        else:
            item_type = selected_item

        # ADD THE MODEL NAME FIELD HERE:
        model_name = st.text_input("Model Name (optional)", help="e.g., Neverfull MM, Speedy 30, Air Force 1, etc.")
        
        selected_platform = st.selectbox("Select Resale Platform (optional)", platform_options)
        
        # If "Other" is selected, show text input
        if selected_platform == "Other":
            platform = st.text_input("Enter Platform Name")
        else:
            platform = selected_platform
        
        # Submit button
        submit_button = st.form_submit_button("Check Risk")
    
    # Process form on submit
        if submit_button:
            if brand and item_type:
                with st.spinner("Analyzing counterfeit risk..."):
                    prompt = build_prompt(brand, item_type, platform, model_name)
                    result = call_ai_model(prompt)
                    # Replace this:
                    # st.markdown(result, unsafe_allow_html=True)
                    # With this:
                    st.components.v1.html(process_html_result(result), height=400, scrolling=True)
                    st.markdown('<div class="disclaimer">This is a preliminary assessment based on general patterns. For high-value purchases, professional authentication is recommended.</div>', unsafe_allow_html=True)
        else:
            st.error("Please provide both brand and item type.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Visual Authentication (Image-based)
with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown("Upload an image of your luxury item for visual authentication analysis.")
    
    with st.form("image_analysis_form"):
        # Brand and item type are still needed for context
        img_brand_options = [
            "",
            # Luxury Fashion
            "Louis Vuitton",
            "Chanel",
            "Dior",
            "Gucci",
            "Hermès",
            "Prada",
            "Balenciaga",
            "Fendi",
            "Saint Laurent",
            "Bottega Veneta",
            "Burberry",
            "Celine",
            "Valentino",
            "Loewe",
            "Givenchy",
            "Versace",
            "Miu Miu",
            "Alexander McQueen",
            "Jacquemus",
            "The Row",
            # Watches & Jewelry
            "Rolex",
            "Cartier",
            "Patek Philippe",
            "Audemars Piguet",
            "Omega",
            "Tiffany & Co.",
            "Van Cleef & Arpels",
            "Bulgari",
            # Streetwear & Contemporary
            "Supreme",
            "Off-White",
            "Bape",
            "Stone Island",
            "Chrome Hearts",
            "Palm Angels",
            "Fear of God",
            "Amiri",
            "Kith",
            "Stüssy",
            "Aimé Leon Dore",
            # Other
            "Other"
        ]
        
        img_item_options = [
            "",
            # Bags & Accessories
            "Handbag",
            "Tote",
            "Crossbody Bag",
            "Backpack",
            "Clutch",
            "Wallet",
            "Card Holder",
            "Belt",
            "Sunglasses",
            "Scarf",
            # Apparel
            "T-Shirt",
            "Hoodie",
            "Sweater/Knitwear",
            "Jacket/Coat",
            "Denim/Jeans",
            "Dress", 
            "Skirt",
            "Pants/Trousers",
            "Button-Up Shirt",
            "Polo Shirt",
            # Footwear
            "Sneakers",
            "Dress Shoes",
            "Heels",
            "Boots",
            "Sandals",
            # Luxury Items
            "Watch",
            "Bracelet",
            "Necklace",
            "Earrings",
            "Ring",
            # Other
            "Other"
        ]
        
        # Form inputs
        img_selected_brand = st.selectbox("Select Brand", img_brand_options, key="img_brand")
        
        # If "Other" is selected, show text input
        if img_selected_brand == "Other":
            img_brand = st.text_input("Enter Brand Name", key="img_brand_other")
        else:
            img_brand = img_selected_brand
        
        img_selected_item = st.selectbox("Select Item Type", img_item_options, key="img_item")
        
        # If "Other" is selected, show text input
        if img_selected_item == "Other":
            img_item_type = st.text_input("Enter Item Type", key="img_item_other")
        else:
            img_item_type = img_selected_item

        img_model_name = st.text_input("Model Name (optional)", key="img_model_name", 
                            help="e.g., Neverfull MM, Speedy 30, Air Force 1, etc.")
        
        # Option to indicate if item is vintage with radio buttons for more options
        vintage_status = st.radio(
            "Is this a vintage item (over 20 years old)?",
            ["Yes", "No", "Unsure"],
            index=2,  # Default to "Unsure"
            help="Select 'Unsure' if you don't know the item's age - the analysis will adapt accordingly"
        )
        
        # If user is unsure about vintage status, provide some guidance
        if vintage_status == "Unsure":
            st.info("""
            **Tips for identifying vintage items:**
            - Check for date codes or serial numbers (often indicate production era)
            - Research specific style elements for the brand/model
            - Look for older versions of brand logos or hardware
            - Examine materials and construction methods that may differ from current production
            
            The analysis will consider both possibilities if you're unsure about the item's age.
            """)
                
        # Display photo guidance based on item type
        if img_selected_item:
            st.markdown("### Photo Guidance")
            st.markdown('<div class="disclaimer">Following these guidelines will improve accuracy and confidence scores:</div>', unsafe_allow_html=True)
            
            # General guidance 
            general_tips = """
            - Use good lighting, preferably natural daylight
            - Take clear, high-resolution photos
            - Include multiple angles if possible
            """
            
            # Item-specific guidance
            if img_selected_item in ["Handbag", "Tote", "Crossbody Bag", "Backpack", "Clutch"]:
                specific_tips = """
                - Photograph the entire bag
                - Include close-ups of hardware (clasps, zippers, etc.)
                - Capture brand logos/monograms
                - Include interior label and/or serial number
                - Show the stitching detail, especially at corners
                """
            elif img_selected_item in ["Wallet", "Card Holder"]:
                specific_tips = """
                - Capture both exterior and interior
                - Include close-ups of any logos/monograms
                - Show any serial numbers or date codes
                - Include details of snaps, clasps, or zippers
                - Photograph the stitching detail
                """
            elif img_selected_item in ["T-Shirt", "Hoodie", "Sweater/Knitwear", "Jacket/Coat", "Denim/Jeans", "Dress", "Skirt", "Pants/Trousers", "Button-Up Shirt", "Polo Shirt"]:
                specific_tips = """
                - Show the entire garment laid flat
                - Capture the interior tags/labels
                - Include close-ups of any logos, embroidery or patches
                - Show any unique hardware (buttons, zippers, snaps)
                - Include details of care/content label and size tag
                """
            elif img_selected_item in ["Sneakers", "Dress Shoes", "Heels", "Boots", "Sandals"]:
                specific_tips = """
                - Photograph the shoes from all angles
                - Include close-ups of the sole pattern
                - Capture the insole with any branding
                - Show any serial numbers or style codes
                - Include details of stitching and material texture
                """
            elif img_selected_item in ["Watch"]:
                specific_tips = """
                - Capture the watch face clearly
                - Include the back of the case
                - Show details of the dial, hands, and markers
                - Include close-ups of any engravings or serial numbers
                - Photograph the crown and pushers (if any)
                """
            elif img_selected_item in ["Bracelet", "Necklace", "Earrings", "Ring"]:
                specific_tips = """
                - Photograph the entire piece
                - Include any hallmarks or stamps
                - Capture close-ups of clasps or fasteners
                - Show any designer signatures or logos
                - Include any authentication cards or packaging
                """
            elif img_selected_item in ["Belt", "Sunglasses", "Scarf"]:
                specific_tips = """
                - Show the entire item
                - Include close-ups of any logos or hardware
                - Capture the inside of the item where applicable
                - Show any serial numbers or authenticity markers
                - Include details of stitching or material texture
                """
            else:
                specific_tips = """
                - Capture the entire item
                - Include close-ups of any brand identifiers
                - Show any serial numbers or authenticity markers
                - Photograph any distinctive hardware or details
                """
            
            # Display the tips
            st.markdown(general_tips)
            st.markdown(specific_tips)
            
        # Image upload
        uploaded_files = st.file_uploader("Upload images of your item (up to 10)", 
                               type=["jpg", "jpeg", "png"], 
                               accept_multiple_files=True,
                               help="Upload multiple photos showing different angles and details")
        
        # Submit button
        img_submit_button = st.form_submit_button("Analyze Image")
    
    # Process image on submit
    if img_submit_button:
        if img_brand and img_item_type and uploaded_files:
            if len(uploaded_files) > 0:
                # Convert vintage_status to boolean flag for internal use
                is_vintage = (vintage_status == "Yes")
                with st.spinner("Analyzing images for authentication markers..."):
                    # Display all uploaded images in a grid
                    cols = st.columns(min(3, len(uploaded_files)))
                    for i, uploaded_file in enumerate(uploaded_files):
                        cols[i % 3].image(uploaded_file, caption=f"Image {i+1}")
                    
                    # Process multiple images (up to 16 maximum allowed by GPT-4o)
                    images_content = []
                    for img in uploaded_files[:16]:  # Limit to 16 images maximum
                        # Compress the image to reduce payload size
                        img_obj = Image.open(img)
                        output = BytesIO()
                        img_obj.save(output, format="JPEG", quality=85)  # Adjust quality as needed
                        img_bytes = output.getvalue()
                        img_str = base64.b64encode(img_bytes).decode()
                        images_content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_str}"
                            }
                        })
                    
                    # Include information about multiple images in the prompt
                    prompt_text = build_image_prompt(img_brand, img_item_type, img_model_name, len(images_content))
                    
                    # Add vintage information if checked
                    if is_vintage:
                        prompt_text += " Please note that this is a vintage item (over 20 years old) and should be assessed with appropriate era-specific authentication markers."
                    
                    # Add the text prompt as the first element
                    content_array = [{"type": "text", "text": prompt_text}] + images_content
                    
                    # Call vision model with multiple images
                    vision_result = call_vision_model_multi(content_array)
                    
                    # Display results
                    st.components.v1.html(process_html_result(vision_result), height=500, scrolling=True)
                    st.markdown('<div class="disclaimer">This visual analysis is a preliminary check only. Professional authentication is recommended for high-value purchases. The tool cannot guarantee authenticity.</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <small>This is a free first-check analysis tool. No definitive claims about authenticity are made. 
    Always authenticate luxury items through professional services before making significant purchases.</small>
    <br>
    <small>© 2025 Luxury Authentication Services</small>
</div>
""", unsafe_allow_html=True)