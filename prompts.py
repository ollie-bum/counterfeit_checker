def build_prompt(brand, item_type, platform=None, model_name=None):
    """
    Builds a prompt for the AI model to analyze counterfeit risk based on item metadata.
    
    Args:
        brand (str): The luxury brand name
        item_type (str): The type of item being checked
        platform (str, optional): The resale platform where the item is being sold
        model_name (str, optional): The specific model name of the item
        
    Returns:
        str: Formatted prompt for the AI model
    """
    return f"""
You are a luxury fashion resale expert. Analyze the counterfeit risk of the following item:

Brand: {brand}
Item Type: {item_type}
Model: {model_name if model_name else 'Not specified'}
Resale Platform: {platform if platform else 'Not specified'}

Based on your expertise, please provide a structured analysis with the following elements:

1. RISK RATING: Clearly state whether this item has a "Low", "Medium", or "High" risk of being counterfeit, based solely on brand-specific counterfeiting patterns for this item type (not condition).
2. EXPLANATION: In 1-2 sentences, explain why you assigned this risk rating, focusing on known counterfeiting statistics for this combination of brand and item type.
3. AUTHENTICATION TIPS: Provide 2-3 specific tips for spotting counterfeits of this exact item type from this brand.
4. PLATFORM RECOMMENDATIONS: List platforms that are higher risk for counterfeits of this item and platforms known for better authentication.

Format your response as clean HTML with a simple structure. Make sure to properly close all HTML tags. Avoid complex nested structures.

Example format:
<div>
<span class="risk-low">RISK: Low</span>
<p class="explanation">Your explanation here.</p>
<h3>Authentication Tips:</h3>
<ul>
<li>Tip 1</li>
<li>Tip 2</li>
<li>Tip 3</li>
</ul>
<h3>Platform Guidance:</h3>
<p>Higher Risk: Platform A, Platform B</p>
<p>Better Authentication: Platform C, Platform D</p>
</div>
"""

def build_image_prompt(brand, item_type, model_name=None, num_images=1):
    """
    Builds a prompt for the vision AI model to analyze counterfeit risk based on multiple images.
    
    Args:
        brand (str): The luxury brand name
        item_type (str): The type of item being checked
        model_name (str, optional): The specific model name of the item
        num_images (int): Number of images uploaded by the user
        
    Returns:
        str: Formatted prompt for the vision AI model
    """
    
    # Base prompt for all items
    model_info = f" {model_name} model" if model_name else ""
    base_prompt = f"""
You are a luxury fashion authentication expert who specializes in visual authentication of {brand} {item_type}{model_info}. 
Analyze all {num_images} provided images of this {brand} {item_type}{model_info} and look for indicators of authenticity or counterfeiting.

The user has uploaded {num_images} image(s) showing different angles and details. Examine all images carefully for your assessment.

CRITICAL INSTRUCTION: You must clearly SEPARATE your assessment of the item's AUTHENTICITY from its CONDITION. An item can be authentic but in poor condition, or counterfeit but in excellent condition. Focus primarily on authenticity markers, not wear and tear.

If the user indicates the age of the item is unknown, take a balanced approach: consider both modern and vintage authentication markers, noting which authentication markers may be era-specific. Be more conservative in your assessment when the age is uncertain, and explain how age might affect your confidence level.

Focus on the following aspects across all images:
1. Brand-specific authentication markers
2. Logo placement, font, and execution
3. Material quality and texture (accounting for age if vintage)
4. Stitching patterns and consistency (not age-related fraying)
5. Hardware design and engravings
6. Serial number or authenticity code format (if visible)
7. Construction methods typical for this brand

Compare details across multiple images when available to form a more complete assessment.
"""

    # Specific guidance based on item category
    specific_guidance = ""
    
    # Bags & Leather Goods
    if item_type in ["Handbag", "Tote", "Crossbody Bag", "Backpack", "Clutch", "Wallet", "Card Holder"]:
        specific_guidance = f"""
For {brand} {item_type}, pay special attention to:
- Hardware specifics: shape, weight appearance, logo engraving depth and font
- Pattern alignment at seams (if applicable)
- Interior lining material, color, and pattern accuracy
- Date codes or serial numbers format and placement
- Stitching pattern and stitch count typical for {brand}
- Edge finishing method specific to {brand}
- Zipper style, pull design, and brand markings
- Brand-specific authentication elements unique to {brand}

NOTE ON VINTAGE ITEMS: If this appears to be a vintage piece, consider era-appropriate materials, construction methods, and hardware. Genuine vintage items may show:
- Natural patina on leather
- Hardware tarnishing
- Edge coating wear or interior wear
- Softened structure
None of these condition issues indicate counterfeiting if other authentication markers are correct.
"""
    
    # Apparel
    elif item_type in ["T-Shirt", "Hoodie", "Sweater/Knitwear", "Jacket/Coat", "Denim/Jeans", "Dress", "Skirt", "Pants/Trousers", "Button-Up Shirt", "Polo Shirt"]:
        specific_guidance = f"""
For {brand} {item_type}, pay special attention to:
- Label font, stitching, and placement accuracy
- Care tag information format and accuracy
- Material composition and weave pattern typical for {brand}
- Print or pattern alignment and proper saturation
- Hardware details (buttons, zippers) and their engravings
- Brand-specific construction details (seam finishes, linings)
- Collar/cuff construction method
- Proper size format and location on tags

NOTE ON VINTAGE ITEMS: Vintage clothing may show:
- Faded labels
- Yellowing or discoloration of white fabric
- Period-appropriate brand labeling (which may differ from current branding)
None of these condition issues indicate counterfeiting if other authentication markers are correct.
"""
    
    # Footwear
    elif item_type in ["Sneakers", "Dress Shoes", "Heels", "Boots", "Sandals"]:
        specific_guidance = f"""
For {brand} {item_type}, pay special attention to:
- Sole pattern and logo placement accuracy
- Insole printing clarity and proper placement
- Box stitching patterns and overall symmetry
- Material texture matching authentic examples
- Tongue label font and stitching precision (for sneakers)
- Heel construction and brand identifiers
- Model-specific design details that are frequently incorrect on counterfeits

NOTE ON VINTAGE ITEMS: Vintage footwear may show:
- Yellowing of white rubber
- Sole separation
- Insole wear or fading
None of these condition issues indicate counterfeiting if other authentication markers are correct.
"""
    
    # Jewelry & Watches
    elif item_type in ["Watch", "Bracelet", "Necklace", "Earrings", "Ring"]:
        specific_guidance = f"""
For {brand} {item_type}, pay special attention to:
- Hallmarks, stamps, or engravings - check for correct font and depth
- Metal finish and specific alloy appearance
- Stone setting technique and quality
- Clasp design and security features
- Serial number format and placement (if visible)
- Brand-specific signatures or markers
- Weight distribution and proportions (even without feeling weight)

NOTE ON VINTAGE ITEMS: Vintage jewelry/watches may show:
- Natural patina on metals
- Stone or crystal scratches
- Clasp wear
None of these condition issues indicate counterfeiting if other authentication markers are correct.
"""
    
    # Accessories
    elif item_type in ["Belt", "Sunglasses", "Scarf"]:
        specific_guidance = f"""
For {brand} {item_type}, pay special attention to:
- Hardware quality and correct brand-specific details
- Material texture and weave consistency
- Logo placement, font, and execution
- Stitching patterns (on belts and textile items)
- Frame hinge quality and temple design (for sunglasses)
- Pattern alignment and color accuracy

NOTE ON VINTAGE ITEMS: Vintage accessories may show:
- Hardware tarnishing
- Color fading or fabric wear
- Loss of rigidity in certain materials
None of these condition issues indicate counterfeiting if other authentication markers are correct.
"""

    # Format and response structure guidance
    formatting_guidance = """
Provide your analysis in the following HTML format:

<div>
    <div>
        <span class="risk-[LEVEL]">AUTHENTICITY ASSESSMENT: [Likely Authentic/Possibly Counterfeit/Likely Counterfeit]</span>
    </div>
    
    <p><span class="confidence-[LEVEL]">Confidence: [High/Medium/Low]</span></p>
    
    <p class="explanation">[1-2 sentence overall assessment on AUTHENTICITY, not condition]</p>
    
    <h3 class="condition-header">Condition Assessment (Separate from Authenticity):</h3>
    <p class="condition-rating">Condition: [Excellent/Good/Fair/Poor]</p>
    <p class="condition-notes">[Brief note on condition aspects like wear, aging, damages]</p>
    
    <h3 class="age-header">Age Assessment:</h3>
    <p class="age-assessment">[Modern/Vintage/Uncertain] - [Brief explanation of age indicators or uncertainty]</p>
    
    <h3 class="flags-header">Authentication Markers:</h3>
    <div>
        <span class="flag-green">[Authentic Feature]</span> [Explanation of correct feature]
    </div>
    <div>
        <span class="flag-red">[Suspicious Feature]</span> [Explanation of concerning feature]
    </div>
    [Add more authentication markers as needed]
    
    <h3 class="visual-header">Authentication Recommendations:</h3>
    <ul>
        <li>[Specific detail to examine further]</li>
        <li>[Another specific detail to examine]</li>
        <li>[Additional check recommendation]</li>
    </ul>
</div>

IMPORTANT:
1. Label your assessment as "Likely Authentic" (low risk), "Possibly Counterfeit" (medium risk), or "Likely Counterfeit" (high risk)
2. Provide a confidence score (High/Medium/Low) based on how clear the visual authentication markers are
3. List at least 1-2 authentic features (green flags) and 1-2 suspicious features (red flags) if visible
4. Be specific about authentication markers, don't make generic statements
5. Don't confuse condition issues with authenticity issues - explicitly separate these
6. Remember that vintage items may have age-appropriate wear while still being authentic

If the image quality is poor or crucial authentication areas aren't visible, indicate this in your assessment and lower your confidence score accordingly.

VERY IMPORTANT: Ensure your HTML is properly formatted and all tags are correctly nested and closed. Use clean, simple HTML structure.
"""

    # Combine all parts of the prompt
    full_prompt = base_prompt + specific_guidance + formatting_guidance
    
    return full_prompt