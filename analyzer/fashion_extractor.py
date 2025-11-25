"""Fashion product extractor for TikTok video analysis.

This module provides comprehensive fashion content detection, product extraction,
trend categorization, and relevance scoring for TikTok videos.
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from rich.console import Console

from models.video import TikTokVideo, ViralCandidate

console = Console()


class FashionExtractor:
    """Analyzes TikTok videos to extract fashion-related information.

    This class provides methods to detect fashion content, extract product mentions,
    categorize fashion trends, and calculate fashion relevance scores.
    """

    def __init__(self):
        """Initialize the FashionExtractor with comprehensive keyword dictionaries."""

        # Clothing items keywords
        self.clothing_items: Set[str] = {
            # Tops
            "shirt", "blouse", "top", "tee", "t-shirt", "tank", "cami", "camisole",
            "crop top", "halter", "tube top", "bodysuit", "corset", "bustier",
            "sweater", "cardigan", "hoodie", "sweatshirt", "pullover", "turtleneck",
            "blazer", "jacket", "coat", "parka", "bomber", "denim jacket", "jean jacket",
            "leather jacket", "trench coat", "peacoat", "windbreaker", "anorak",
            "vest", "waistcoat", "gilet",

            # Bottoms
            "pants", "jeans", "trousers", "slacks", "chinos", "khakis",
            "leggings", "tights", "joggers", "sweatpants", "cargo pants",
            "shorts", "skirt", "mini skirt", "midi skirt", "maxi skirt",
            "pencil skirt", "pleated skirt", "denim skirt", "tennis skirt",

            # Dresses & Jumpsuits
            "dress", "gown", "sundress", "maxi dress", "midi dress", "mini dress",
            "slip dress", "wrap dress", "shirt dress", "bodycon dress", "a-line dress",
            "cocktail dress", "evening dress", "party dress", "prom dress",
            "jumpsuit", "romper", "playsuit", "overalls", "dungarees",

            # Outerwear
            "puffer", "puffer jacket", "down jacket", "raincoat", "poncho",
            "cape", "shawl", "wrap", "kimono", "robe",

            # Activewear
            "sports bra", "workout top", "athletic wear", "gym wear",
            "yoga pants", "bike shorts", "running shorts", "tracksuit",

            # Innerwear/Sleepwear
            "bra", "lingerie", "underwear", "pajamas", "nightgown", "sleepwear",

            # Seasonal
            "swimsuit", "bikini", "bathing suit", "swim shorts", "boardshorts",
        }

        # Accessories keywords
        self.accessories: Set[str] = {
            # Bags
            "bag", "purse", "handbag", "tote", "clutch", "crossbody",
            "shoulder bag", "satchel", "backpack", "messenger bag",
            "duffle", "weekender", "fanny pack", "belt bag", "bum bag",
            "pouch", "wallet", "coin purse",

            # Footwear
            "shoes", "sneakers", "trainers", "kicks", "heels", "pumps",
            "stilettos", "wedges", "platforms", "flats", "loafers",
            "oxfords", "brogues", "mules", "slides", "sandals",
            "flip flops", "boots", "ankle boots", "knee boots", "combat boots",
            "chelsea boots", "uggs", "doc martens", "dr martens", "crocs",
            "slippers", "espadrilles", "mary janes", "ballet flats",

            # Jewelry
            "jewelry", "jewellery", "necklace", "pendant", "chain",
            "bracelet", "bangle", "cuff", "ring", "earrings", "hoops",
            "studs", "anklet", "brooch", "pin",

            # Other Accessories
            "hat", "cap", "beanie", "beret", "bucket hat", "baseball cap",
            "fedora", "sun hat", "visor", "headband", "hair clip",
            "scrunchie", "hair tie", "bandana", "scarf", "tie",
            "bow tie", "belt", "suspenders", "gloves", "mittens",
            "socks", "stockings", "tights", "sunglasses", "glasses",
            "watch", "smartwatch",
        }

        # Fashion brands keywords
        self.brands: Set[str] = {
            # Fast Fashion
            "zara", "h&m", "h and m", "shein", "forever21", "forever 21",
            "uniqlo", "gap", "old navy", "target", "walmart",
            "primark", "asos", "boohoo", "prettylittlething", "plt",
            "fashion nova", "fashionnova", "missguided", "nasty gal",
            "urban outfitters", "topshop", "mango", "pull&bear",

            # Mid-range
            "reformation", "everlane", "cos", "arket", "massimo dutti",
            "reiss", "whistles", "& other stories", "sezane",
            "abercrombie", "hollister", "american eagle", "ae",
            "express", "j.crew", "jcrew", "madewell", "anthropologie",

            # Athleisure
            "nike", "adidas", "puma", "reebok", "under armour",
            "lululemon", "gymshark", "fabletics", "athleta",
            "alo", "alo yoga", "outdoor voices", "sweaty betty",

            # Denim
            "levi's", "levis", "wrangler", "lee", "diesel", "ag jeans",
            "citizens of humanity", "frame", "mother denim", "paige",

            # Luxury/Designer
            "gucci", "prada", "chanel", "dior", "louis vuitton", "lv",
            "hermes", "hermès", "fendi", "versace", "balenciaga",
            "saint laurent", "ysl", "bottega veneta", "celine", "céline",
            "givenchy", "valentino", "burberry", "moncler", "canada goose",

            # Contemporary
            "zimmermann", "ganni", "staud", "jacquemus", "rotate",
            "realisation par", "rixo", "free people", "farm rio",

            # Streetwear
            "supreme", "stussy", "bape", "off-white", "palace",
            "carhartt", "dickies", "kith", "aime leon dore",

            # Accessories/Shoes
            "michael kors", "mk", "coach", "kate spade", "tory burch",
            "steve madden", "sam edelman", "jeffrey campbell",
            "dr martens", "converse", "vans", "new balance",
            "allbirds", "rothys", "rothy's",

            # Online/Indie
            "revolve", "shopbop", "net-a-porter", "farfetch",
            "ssense", "nordstrom", "saks", "bloomingdale's",
            "princess polly", "showpo", "beginning boutique",
        }

        # Style categories/trends keywords
        self.style_categories: Dict[str, Set[str]] = {
            "streetwear": {
                "streetwear", "street style", "urban", "hypebeast", "hype",
                "sneakerhead", "oversized", "baggy", "skate", "skatewear",
                "hip hop", "rapper", "90s hip hop", "grunge",
            },
            "y2k": {
                "y2k", "2000s", "early 2000s", "00s", "paris hilton",
                "juicy couture", "low rise", "butterfly", "rhinestone",
                "velour", "tracksuit", "baby tee", "mini skirt",
            },
            "minimalist": {
                "minimalist", "minimal", "clean", "simple", "neutral",
                "capsule wardrobe", "timeless", "classic", "elegant",
                "scandinavian", "scandi", "monochrome", "all black",
            },
            "coquette": {
                "coquette", "balletcore", "ballet", "ribbon", "bow",
                "feminine", "girly", "princess", "fairy", "lace",
                "ruffle", "pastel", "pink", "romantic", "dainty",
            },
            "cottage core": {
                "cottagecore", "cottage core", "cottagewave", "prairie",
                "floral", "vintage", "pastoral", "countryside", "folk",
                "linen", "embroidery", "puff sleeve", "milkmaid",
            },
            "dark academia": {
                "dark academia", "academia", "scholarly", "preppy",
                "ivy league", "oxford", "vintage academic", "tweed",
                "blazer", "plaid", "argyle", "loafer", "bookish",
            },
            "coastal": {
                "coastal", "coastal grandmother", "coastal vibes", "beach",
                "nautical", "maritime", "linen", "breezy", "effortless",
                "vacation", "resort", "mediterranean", "riviera",
            },
            "boho": {
                "boho", "bohemian", "boho chic", "hippie", "free spirit",
                "festival", "coachella", "flowy", "fringe", "crochet",
                "paisley", "ethnic", "tribal", "maxi", "bell bottoms",
            },
            "athleisure": {
                "athleisure", "sporty", "athletic", "gym", "workout",
                "activewear", "yoga", "pilates", "running", "training",
                "performance", "tech wear", "moisture wicking",
            },
            "glamorous": {
                "glam", "glamorous", "luxe", "luxury", "bougie",
                "dressy", "fancy", "cocktail", "evening", "sparkle",
                "sequin", "satin", "silk", "velvet", "elegant",
            },
            "edgy": {
                "edgy", "rock", "punk", "goth", "gothic", "emo",
                "alternative", "alt", "grunge", "biker", "leather",
                "studded", "chain", "dark", "all black", "combat boots",
            },
            "preppy": {
                "preppy", "prep", "ivy", "collegiate", "tennis",
                "country club", "polo", "cable knit", "argyle",
                "blazer", "loafer", "boat shoe", "varsity", "plaid",
            },
        }

        # Fashion action keywords (haul, styling, etc.)
        self.fashion_actions: Set[str] = {
            "haul", "try on", "tryon", "try-on", "styling", "outfit",
            "ootd", "outfit of the day", "look", "get ready with me",
            "grwm", "get dressed", "style", "fashion",
            "lookbook", "capsule", "wardrobe", "closet",
            "thrift", "thrifted", "vintage", "secondhand", "preloved",
            "shopping", "shop", "unboxing", "review", "fit check",
            "what i wore", "wiw", "fashion week", "runway",
            "dupe", "affordable", "budget", "cheap", "under",
            "inspired", "recreation", "recreate", "celebrity style",
            "get the look", "style inspo", "inspiration",
            "transition", "fall fashion", "winter fashion",
            "spring fashion", "summer fashion", "seasonal",
            "trend", "trending", "viral", "must have",
            "essential", "staple", "piece", "find", "score",
        }

        # Fashion-related hashtags (compiled for faster matching)
        self.fashion_hashtags: Set[str] = {
            "fashion", "style", "ootd", "outfit", "fashiontiktok",
            "fashioninspo", "styletips", "fashiontrends", "fashionhaul",
            "clothinghaul", "outfitinspo", "outfitideas", "fashiongram",
            "styleinspo", "fashionblogger", "fashionista", "fashionable",
            "instafashion", "streetstyle", "whatiwore", "outfitoftheday",
            "lookbook", "fashiondiaries", "currentlywearing", "wiw",
            "grwm", "getreadywithme", "tryon", "tryonhaul", "haul",
            "shoppinghaul", "fashionfinds", "affordablefashion",
            "budgetfashion", "thrifted", "thrifthaul", "vintagehaul",
        }

        console.log("[green]FashionExtractor initialized with comprehensive keyword dictionaries[/green]")

    def is_fashion_content(self, video: TikTokVideo) -> bool:
        """Determine if a video contains fashion-related content.

        Args:
            video: TikTokVideo object to analyze

        Returns:
            True if the video is fashion-related, False otherwise
        """
        description_lower = video.description.lower()
        hashtags_lower = [tag.lower() for tag in video.hashtags]

        # Check hashtags first (most reliable indicator)
        for hashtag in hashtags_lower:
            if hashtag in self.fashion_hashtags:
                console.log(f"[cyan]Fashion content detected via hashtag: #{hashtag}[/cyan]")
                return True

        # Check for fashion actions in description
        for action in self.fashion_actions:
            if action in description_lower:
                console.log(f"[cyan]Fashion content detected via action: '{action}'[/cyan]")
                return True

        # Check for clothing items
        clothing_count = sum(1 for item in self.clothing_items if item in description_lower)
        if clothing_count >= 2:
            console.log(f"[cyan]Fashion content detected: {clothing_count} clothing items mentioned[/cyan]")
            return True

        # Check for brands
        for brand in self.brands:
            if brand in description_lower:
                console.log(f"[cyan]Fashion content detected via brand: {brand}[/cyan]")
                return True

        # Check for accessories
        accessory_count = sum(1 for acc in self.accessories if acc in description_lower)
        if accessory_count >= 2:
            console.log(f"[cyan]Fashion content detected: {accessory_count} accessories mentioned[/cyan]")
            return True

        # Check for style category keywords in hashtags
        for category, keywords in self.style_categories.items():
            for keyword in keywords:
                if any(keyword in tag for tag in hashtags_lower):
                    console.log(f"[cyan]Fashion content detected via style: {category}[/cyan]")
                    return True

        console.log("[dim]No fashion content detected[/dim]")
        return False

    def extract_products(self, description: str, hashtags: List[str]) -> List[Dict[str, str]]:
        """Extract fashion product mentions from video description and hashtags.

        Args:
            description: Video description text
            hashtags: List of hashtag strings

        Returns:
            List of dictionaries containing detected products with type and name
        """
        products: List[Dict[str, str]] = []
        description_lower = description.lower()
        hashtags_lower = [tag.lower() for tag in hashtags]
        combined_text = f"{description_lower} {' '.join(hashtags_lower)}"

        # Extract clothing items
        for item in self.clothing_items:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(item) + r'\b'
            if re.search(pattern, combined_text):
                products.append({
                    "type": "clothing",
                    "name": item,
                    "source": "description" if item in description_lower else "hashtag"
                })

        # Extract accessories
        for accessory in self.accessories:
            pattern = r'\b' + re.escape(accessory) + r'\b'
            if re.search(pattern, combined_text):
                products.append({
                    "type": "accessory",
                    "name": accessory,
                    "source": "description" if accessory in description_lower else "hashtag"
                })

        # Extract brand mentions
        for brand in self.brands:
            pattern = r'\b' + re.escape(brand) + r'\b'
            if re.search(pattern, combined_text):
                products.append({
                    "type": "brand",
                    "name": brand,
                    "source": "description" if brand in description_lower else "hashtag"
                })

        # Remove duplicates while preserving order
        seen = set()
        unique_products = []
        for product in products:
            key = (product["type"], product["name"])
            if key not in seen:
                seen.add(key)
                unique_products.append(product)

        if unique_products:
            console.log(f"[green]Extracted {len(unique_products)} products[/green]")

        return unique_products

    def categorize_trend(self, hashtags: List[str], description: str) -> str:
        """Categorize the fashion trend/style of the content.

        Args:
            hashtags: List of hashtag strings
            description: Video description text

        Returns:
            Trend category name or "general" if no specific trend detected
        """
        hashtags_lower = [tag.lower() for tag in hashtags]
        description_lower = description.lower()
        combined_text = f"{description_lower} {' '.join(hashtags_lower)}"

        # Score each category based on keyword matches
        category_scores: Dict[str, int] = {}

        for category, keywords in self.style_categories.items():
            score = 0
            matched_keywords = []

            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = len(re.findall(pattern, combined_text))
                if matches > 0:
                    score += matches
                    matched_keywords.append(keyword)

            if score > 0:
                category_scores[category] = score
                console.log(f"[dim]Category '{category}' score: {score} (matched: {', '.join(matched_keywords[:3])})[/dim]")

        # Return category with highest score
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            console.log(f"[green]Trend categorized as: {best_category[0]} (score: {best_category[1]})[/green]")
            return best_category[0]

        console.log("[dim]No specific trend category detected, using 'general'[/dim]")
        return "general"

    def calculate_fashion_score(self, video: TikTokVideo) -> float:
        """Calculate a fashion relevance score for the video.

        The score is based on:
        - Number of fashion hashtags (0-30 points)
        - Number of fashion actions mentioned (0-20 points)
        - Number of products detected (0-30 points)
        - Presence of brand mentions (0-10 points)
        - Style category specificity (0-10 points)

        Args:
            video: TikTokVideo object to analyze

        Returns:
            Fashion relevance score (0-100)
        """
        score = 0.0
        description_lower = video.description.lower()
        hashtags_lower = [tag.lower() for tag in video.hashtags]

        # Score fashion hashtags (up to 30 points)
        fashion_tag_count = sum(1 for tag in hashtags_lower if tag in self.fashion_hashtags)
        hashtag_score = min(fashion_tag_count * 5, 30)
        score += hashtag_score
        console.log(f"[dim]Hashtag score: {hashtag_score} ({fashion_tag_count} fashion hashtags)[/dim]")

        # Score fashion actions (up to 20 points)
        action_count = sum(1 for action in self.fashion_actions if action in description_lower)
        action_score = min(action_count * 5, 20)
        score += action_score
        console.log(f"[dim]Action score: {action_score} ({action_count} fashion actions)[/dim]")

        # Score product mentions (up to 30 points)
        products = self.extract_products(video.description, video.hashtags)
        product_score = min(len(products) * 3, 30)
        score += product_score
        console.log(f"[dim]Product score: {product_score} ({len(products)} products)[/dim]")

        # Score brand mentions (up to 10 points)
        brand_count = sum(1 for brand in self.brands
                         if brand in description_lower or any(brand in tag for tag in hashtags_lower))
        brand_score = min(brand_count * 5, 10)
        score += brand_score
        console.log(f"[dim]Brand score: {brand_score} ({brand_count} brands)[/dim]")

        # Score style category (up to 10 points)
        trend = self.categorize_trend(video.hashtags, video.description)
        category_score = 10 if trend != "general" else 5
        score += category_score
        console.log(f"[dim]Category score: {category_score} (trend: {trend})[/dim]")

        console.log(f"[green]Total fashion score: {score}/100[/green]")
        return score

    def enrich_viral_candidate(self, candidate: ViralCandidate) -> ViralCandidate:
        """Enrich a ViralCandidate with fashion-specific data.

        This method populates the fashion-related fields of a ViralCandidate:
        - detected_products: List of product dictionaries
        - fashion_keywords: List of relevant keywords found
        - trend_category: Fashion trend/style category

        Args:
            candidate: ViralCandidate object to enrich

        Returns:
            The enriched ViralCandidate object
        """
        video = candidate.video

        console.log(f"[cyan]Enriching viral candidate: {video.video_id}[/cyan]")

        # Extract products
        products = self.extract_products(video.description, video.hashtags)
        candidate.detected_products = [p["name"] for p in products]

        # Extract fashion keywords
        keywords = []
        description_lower = video.description.lower()
        hashtags_lower = [tag.lower() for tag in video.hashtags]
        combined_text = f"{description_lower} {' '.join(hashtags_lower)}"

        # Add fashion action keywords
        keywords.extend([action for action in self.fashion_actions if action in combined_text])

        # Add style category keywords found
        for category, category_keywords in self.style_categories.items():
            for keyword in category_keywords:
                if keyword in combined_text and keyword not in keywords:
                    keywords.append(keyword)

        # Limit to top 10 most relevant keywords
        candidate.fashion_keywords = keywords[:10]

        # Categorize trend
        candidate.trend_category = self.categorize_trend(video.hashtags, video.description)

        console.log(f"[green]Enrichment complete: {len(candidate.detected_products)} products, "
                   f"{len(candidate.fashion_keywords)} keywords, category: {candidate.trend_category}[/green]")

        return candidate

    def get_all_keywords(self) -> Dict[str, int]:
        """Get summary of all keyword dictionaries.

        Returns:
            Dictionary with keyword category names and counts
        """
        return {
            "clothing_items": len(self.clothing_items),
            "accessories": len(self.accessories),
            "brands": len(self.brands),
            "style_categories": len(self.style_categories),
            "total_style_keywords": sum(len(keywords) for keywords in self.style_categories.values()),
            "fashion_actions": len(self.fashion_actions),
            "fashion_hashtags": len(self.fashion_hashtags),
        }

    def search_keywords(self, query: str) -> Dict[str, List[str]]:
        """Search for keywords matching a query across all dictionaries.

        Args:
            query: Search query string

        Returns:
            Dictionary with categories and matching keywords
        """
        query_lower = query.lower()
        results: Dict[str, List[str]] = {}

        # Search clothing items
        matches = [item for item in self.clothing_items if query_lower in item]
        if matches:
            results["clothing_items"] = matches

        # Search accessories
        matches = [acc for acc in self.accessories if query_lower in acc]
        if matches:
            results["accessories"] = matches

        # Search brands
        matches = [brand for brand in self.brands if query_lower in brand]
        if matches:
            results["brands"] = matches

        # Search fashion actions
        matches = [action for action in self.fashion_actions if query_lower in action]
        if matches:
            results["fashion_actions"] = matches

        # Search style categories
        for category, keywords in self.style_categories.items():
            matches = [kw for kw in keywords if query_lower in kw]
            if matches:
                results[f"style_{category}"] = matches

        return results
