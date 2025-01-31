
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re
import sqlite3

from .errors import ValidationError
from .models import AnalysisType, AnalysisRequest

class RequestValidator:

    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
        # Common validation patterns
        self.SYMBOL_PATTERN = re.compile(r'^[A-Z]{1,5}$')
        self.DATE_FORMAT = '%Y-%m-%d'
        
        # Validation constraints
        self.MAX_LOOKBACK_DAYS = 365 * 5  # 5 years
        self.MIN_LOOKBACK_DAYS = 1
        
        # Cache of valid symbols (updated periodically)
        self._valid_symbols: Optional[List[str]] = None
        self._symbols_last_updated: Optional[datetime] = None
    
    def validate_analysis_request(self, request: Dict[str, Any]) -> None:
       
        required_fields = ['symbol', 'analysis_type']
        self._validate_required_fields(request, required_fields)
        
        # Validate symbol
        self._validate_symbol(request['symbol'])
        
        # Validate analysis type
        self._validate_analysis_type(request['analysis_type'])
        
        # Validate dates if present
        if 'start_date' in request or 'end_date' in request:
            self._validate_date_range(
                request.get('start_date'),
                request.get('end_date')
            )
        
        # Validate optional parameters
        if 'params' in request:
            self._validate_analysis_params(
                request['analysis_type'],
                request['params']
            )
    
    def _validate_required_fields(
        self,
        request: Dict[str, Any],
        required_fields: List[str]
    ) -> None:
        """Validate presence of required fields"""
        missing_fields = [
            field for field in required_fields
            if field not in request or request[field] is None
        ]
        
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
    
    def _validate_symbol(self, symbol: str) -> None:
        """Validate stock symbol"""
        # Check format
        if not self.SYMBOL_PATTERN.match(symbol):
            raise ValidationError(
                f"Invalid symbol format: {symbol}. "
                "Must be 1-5 uppercase letters."
            )
        
        # Check if symbol exists in database
        if not self._is_valid_symbol(symbol):
            raise ValidationError(f"Symbol not found: {symbol}")
    
    def _validate_analysis_type(self, analysis_type: str) -> None:
        """Validate analysis type"""
        valid_types = {
            'technical', 'sentiment', 'ml', 'options',
            'portfolio', 'risk', 'all'
        }
        
        if analysis_type not in valid_types:
            raise ValidationError(
                f"Invalid analysis type: {analysis_type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )
    
    def _validate_date_range(
        self,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> None:
        """Validate date range"""
        try:
            if start_date:
                start = datetime.strptime(start_date, self.DATE_FORMAT)
            else:
                start = datetime.now() - timedelta(days=90)  # Default 90 days
            
            if end_date:
                end = datetime.strptime(end_date, self.DATE_FORMAT)
            else:
                end = datetime.now()
            
            # Check date order
            if start > end:
                raise ValidationError(
                    "Start date must be before end date"
                )
            
            # Check range limits
            days_diff = (end - start).days
            if days_diff > self.MAX_LOOKBACK_DAYS:
                raise ValidationError(
                    f"Date range too large. Maximum is {self.MAX_LOOKBACK_DAYS} days"
                )
            
            if days_diff < self.MIN_LOOKBACK_DAYS:
                raise ValidationError(
                    f"Date range too small. Minimum is {self.MIN_LOOKBACK_DAYS} day"
                )
            
        except ValueError as e:
            raise ValidationError(
                f"Invalid date format. Use {self.DATE_FORMAT}"
            ) from e
    
    def _validate_analysis_params(
        self,
        analysis_type: str,
        params: Dict[str, Any]
    ) -> None:
        """Validate analysis-specific parameters"""
        if analysis_type == 'technical':
            self._validate_technical_params(params)
        elif analysis_type == 'ml':
            self._validate_ml_params(params)
        elif analysis_type == 'options':
            self._validate_options_params(params)
    
    def _validate_technical_params(self, params: Dict[str, Any]) -> None:
        """Validate technical analysis parameters"""
        valid_params = {
            'indicators',
            'period',
            'moving_average_periods'
        }
        
        invalid_params = set(params.keys()) - valid_params
        if invalid_params:
            raise ValidationError(
                f"Invalid technical analysis parameters: {', '.join(invalid_params)}"
            )
        
        # Validate specific parameters
        if 'period' in params:
            period = params['period']
            if not isinstance(period, int) or period < 1:
                raise ValidationError(
                    "Period must be a positive integer"
                )
    
    def _validate_ml_params(self, params: Dict[str, Any]) -> None:
        """Validate machine learning parameters"""
        valid_params = {
            'prediction_days',
            'confidence_threshold',
            'features'
        }
        
        invalid_params = set(params.keys()) - valid_params
        if invalid_params:
            raise ValidationError(
                f"Invalid ML parameters: {', '.join(invalid_params)}"
            )
        
        # Validate prediction days
        if 'prediction_days' in params:
            days = params['prediction_days']
            if not isinstance(days, int) or days < 1 or days > 30:
                raise ValidationError(
                    "prediction_days must be an integer between 1 and 30"
                )
    
    def _validate_options_params(self, params: Dict[str, Any]) -> None:
        """Validate options analysis parameters"""
        valid_params = {
            'expiration_range',
            'strike_range',
            'option_types'
        }
        
        invalid_params = set(params.keys()) - valid_params
        if invalid_params:
            raise ValidationError(
                f"Invalid options parameters: {', '.join(invalid_params)}"
            )
        
        # Validate option types
        if 'option_types' in params:
            valid_types = {'call', 'put', 'both'}
            if params['option_types'] not in valid_types:
                raise ValidationError(
                    f"option_types must be one of: {', '.join(valid_types)}"
                )
    
    def _is_valid_symbol(self, symbol: str) -> bool:
        """Check if symbol exists in database"""
        # Update cache if needed
        if (self._valid_symbols is None or
            self._symbols_last_updated is None or
            datetime.now() - self._symbols_last_updated > timedelta(hours=1)):
            self._update_symbol_cache()
        
        return symbol in (self._valid_symbols or set())
    
    def _update_symbol_cache(self) -> None:
        """Update cache of valid symbols"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT symbol FROM stocks")
                self._valid_symbols = {row[0] for row in cursor.fetchall()}
                self._symbols_last_updated = datetime.now()
                
        except sqlite3.Error as e:
            raise ValidationError(
                f"Database error while validating symbol: {str(e)}"
            )