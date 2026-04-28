from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any
import re
import json

class PhoneValidationInput(BaseModel):
    """Input schema for Multi-Source Phone Validator Tool."""
    phone_number: str = Field(description="The phone number to validate")
    company_name: str = Field(description="Company name for context")
    phone_source: str = Field(description="Source where number was found (datagma, rocketreach, prospeo, web_scrape, etc.)")
    country_code: str = Field(default="US", description="Expected country code (US, UK, CA, etc.)")

class MultiSourcePhoneValidatorTool(BaseTool):
    """Tool for validating and scoring phone numbers from various sources with business context."""

    name: str = "multi_source_phone_validator"
    description: str = (
        "Validates phone numbers from various sources and provides confidence scoring, "
        "business likelihood assessment, and priority recommendations for sales teams. "
        "Supports US, UK, CA formats with source reliability scoring."
    )
    args_schema: Type[BaseModel] = PhoneValidationInput

    def _run(self, phone_number: str, company_name: str, phone_source: str, country_code: str = "US") -> str:
        try:
            # Clean the phone number
            cleaned_number = self._clean_phone_number(phone_number)
            
            # Validate format and get formatted number
            format_result = self._validate_format(cleaned_number, country_code)
            
            # Score source reliability
            source_score = self._score_source_reliability(phone_source)
            
            # Classify phone type and business likelihood
            phone_type, business_score = self._classify_phone_type(cleaned_number, country_code)
            
            # Calculate overall confidence score
            confidence_score = self._calculate_confidence_score(
                format_result["is_valid"], 
                source_score, 
                business_score,
                format_result["format_quality"]
            )
            
            # Generate validation notes
            validation_notes = self._generate_validation_notes(
                format_result, phone_type, source_score, business_score
            )
            
            # Determine recommendation
            recommendation = self._get_recommendation(confidence_score, business_score, phone_type)
            
            result = {
                "is_valid": format_result["is_valid"],
                "formatted_number": format_result["formatted_number"],
                "confidence_score": confidence_score,
                "phone_type": phone_type,
                "business_likelihood": business_score,
                "validation_notes": validation_notes,
                "recommended_use": recommendation
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                "is_valid": False,
                "formatted_number": phone_number,
                "confidence_score": 1,
                "phone_type": "unknown",
                "business_likelihood": 1,
                "validation_notes": f"Validation error: {str(e)}",
                "recommended_use": "do_not_use"
            }
            return json.dumps(error_result, indent=2)

    def _clean_phone_number(self, phone_number: str) -> str:
        """Remove invalid characters and normalize the phone number."""
        # Remove common invalid characters but keep +, -, (, ), spaces
        cleaned = re.sub(r'[^\d\+\-\(\)\s]', '', phone_number.strip())
        return cleaned

    def _validate_format(self, phone_number: str, country_code: str) -> Dict[str, Any]:
        """Validate phone number format based on country code."""
        # Remove all non-digit characters for digit counting
        digits_only = re.sub(r'\D', '', phone_number)
        
        format_quality = 0
        formatted_number = phone_number
        is_valid = False
        
        if country_code.upper() == "US":
            is_valid, formatted_number, format_quality = self._validate_us_format(phone_number, digits_only)
        elif country_code.upper() == "UK":
            is_valid, formatted_number, format_quality = self._validate_uk_format(phone_number, digits_only)
        elif country_code.upper() == "CA":
            # Canada uses same format as US
            is_valid, formatted_number, format_quality = self._validate_us_format(phone_number, digits_only)
        else:
            # Basic international validation
            if len(digits_only) >= 7 and len(digits_only) <= 15:
                is_valid = True
                format_quality = 5
                if phone_number.startswith('+'):
                    format_quality = 7
                    
        return {
            "is_valid": is_valid,
            "formatted_number": formatted_number,
            "format_quality": format_quality
        }

    def _validate_us_format(self, phone_number: str, digits_only: str) -> tuple:
        """Validate US phone number format."""
        is_valid = False
        formatted_number = phone_number
        format_quality = 0
        
        # US numbers should have 10 or 11 digits (with country code)
        if len(digits_only) == 10:
            # Standard US format
            area_code = digits_only[:3]
            exchange = digits_only[3:6]
            number = digits_only[6:10]
            
            # Check for valid area code (not starting with 0 or 1)
            if area_code[0] not in ['0', '1'] and exchange[0] not in ['0', '1']:
                is_valid = True
                formatted_number = f"({area_code}) {exchange}-{number}"
                format_quality = 7
                
                # Higher quality if already properly formatted
                if phone_number.startswith('+1'):
                    format_quality = 9
                    formatted_number = f"+1 ({area_code}) {exchange}-{number}"
                    
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            # US number with country code
            area_code = digits_only[1:4]
            exchange = digits_only[4:7]
            number = digits_only[7:11]
            
            if area_code[0] not in ['0', '1'] and exchange[0] not in ['0', '1']:
                is_valid = True
                formatted_number = f"+1 ({area_code}) {exchange}-{number}"
                format_quality = 9
                
        return is_valid, formatted_number, format_quality

    def _validate_uk_format(self, phone_number: str, digits_only: str) -> tuple:
        """Validate UK phone number format."""
        is_valid = False
        formatted_number = phone_number
        format_quality = 0
        
        # UK numbers typically 10-11 digits
        if len(digits_only) >= 10 and len(digits_only) <= 11:
            is_valid = True
            format_quality = 5
            
            # Higher quality if starts with +44
            if phone_number.startswith('+44'):
                format_quality = 8
                
            # Common UK mobile prefixes (07)
            if digits_only.startswith('07') or digits_only.startswith('4407'):
                format_quality += 1
                
        return is_valid, formatted_number, format_quality

    def _score_source_reliability(self, phone_source: str) -> int:
        """Score source reliability from 1-10."""
        source_scores = {
            "datagma": 8,
            "rocketreach": 7,
            "prospeo": 6,
            "linkedin": 5,
            "web_scrape": 4,
            "social_media": 3,
            "directory": 6,
            "company_website": 7,
            "verified_database": 9,
            "manual_entry": 5
        }
        
        source_lower = phone_source.lower()
        for source, score in source_scores.items():
            if source in source_lower:
                return score
                
        return 3  # Default low score for unknown sources

    def _classify_phone_type(self, phone_number: str, country_code: str) -> tuple:
        """Classify phone type and assess business likelihood."""
        digits_only = re.sub(r'\D', '', phone_number)
        phone_type = "unknown"
        business_score = 5  # Default neutral score
        
        if country_code.upper() == "US":
            phone_type, business_score = self._classify_us_phone(digits_only)
        elif country_code.upper() == "UK":
            phone_type, business_score = self._classify_uk_phone(digits_only)
        elif country_code.upper() == "CA":
            phone_type, business_score = self._classify_us_phone(digits_only)
            
        return phone_type, business_score

    def _classify_us_phone(self, digits_only: str) -> tuple:
        """Classify US phone number type."""
        if len(digits_only) >= 10:
            # Get the relevant digits (last 10 for US numbers)
            relevant_digits = digits_only[-10:]
            area_code = relevant_digits[:3]
            exchange = relevant_digits[3:6]
            
            # Toll-free numbers
            toll_free_codes = ['800', '833', '844', '855', '866', '877', '888']
            if area_code in toll_free_codes:
                return "toll_free", 9
                
            # Mobile prefixes (rough approximation)
            mobile_exchanges = ['310', '323', '424', '510', '415', '628', '650', '669', '408']
            if exchange[:3] in mobile_exchanges or area_code in ['310', '323', '424']:
                return "mobile", 4
                
            # Business-like patterns (repeated digits often indicate main lines)
            if len(set(relevant_digits[6:])) == 1:  # Last 4 digits same
                return "main", 7
                
            # Geographic business indicators
            business_area_codes = ['212', '213', '312', '313', '404', '415', '617', '713', '214']
            if area_code in business_area_codes:
                return "direct", 6
                
        return "unknown", 5

    def _classify_uk_phone(self, digits_only: str) -> tuple:
        """Classify UK phone number type."""
        if len(digits_only) >= 10:
            # Remove country code if present
            if digits_only.startswith('44'):
                digits_only = digits_only[2:]
            elif digits_only.startswith('044'):
                digits_only = digits_only[3:]
                
            # Mobile numbers (07)
            if digits_only.startswith('07'):
                return "mobile", 4
                
            # London numbers (020)
            if digits_only.startswith('020'):
                return "direct", 7
                
            # Toll-free (0800, 0808)
            if digits_only.startswith('0800') or digits_only.startswith('0808'):
                return "toll_free", 9
                
            # Business numbers (01, 02)
            if digits_only.startswith('01') or digits_only.startswith('02'):
                return "main", 6
                
        return "unknown", 5

    def _calculate_confidence_score(self, is_valid: bool, source_score: int, 
                                  business_score: int, format_quality: int) -> int:
        """Calculate overall confidence score from 1-10."""
        if not is_valid:
            return 1
            
        # Weighted average
        confidence = (source_score * 0.3 + business_score * 0.3 + format_quality * 0.4)
        
        # Ensure score is between 1-10
        confidence = max(1, min(10, round(confidence)))
        
        return int(confidence)

    def _generate_validation_notes(self, format_result: Dict, phone_type: str, 
                                 source_score: int, business_score: int) -> str:
        """Generate detailed validation notes."""
        notes = []
        
        if format_result["is_valid"]:
            notes.append(f"✓ Valid phone format (quality: {format_result['format_quality']}/10)")
        else:
            notes.append("✗ Invalid phone format")
            
        notes.append(f"Source reliability: {source_score}/10")
        notes.append(f"Business likelihood: {business_score}/10")
        notes.append(f"Classified as: {phone_type}")
        
        if phone_type == "toll_free":
            notes.append("⭐ Toll-free number - likely customer service line")
        elif phone_type == "mobile":
            notes.append("📱 Mobile number - may be personal")
        elif phone_type == "main":
            notes.append("🏢 Main business line indicator")
        elif phone_type == "direct":
            notes.append("📞 Direct line indicator")
            
        return "; ".join(notes)

    def _get_recommendation(self, confidence_score: int, business_score: int, phone_type: str) -> str:
        """Determine call priority recommendation."""
        if confidence_score >= 8 and business_score >= 7:
            return "high_priority"
        elif confidence_score >= 6 and business_score >= 5:
            return "medium_priority"
        elif confidence_score >= 4:
            return "low_priority"
        else:
            return "do_not_use"