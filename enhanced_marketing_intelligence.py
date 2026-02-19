"""
Enhanced Marketing Intelligence Engine
Provides channel performance analysis, timing intelligence, and budget allocation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MarketingIntelligenceEngine:
    """
    Marketing Intelligence Engine for analyzing channel performance,
    timing effectiveness, and budget allocation optimization
    """
    
    def __init__(self, conn):
        """
        Initialize the Marketing Intelligence Engine
        
        Args:
            conn: Database connection
        """
        self.conn = conn
        self.marketing_data = None
        self.admissions_data = None
        
    def load_data(self, programs: List[str]) -> bool:
        """
        Load marketing and admissions data for specified programs
        
        Args:
            programs: List of program names to load data for
            
        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            # Load marketing spend data
            programs_str = "', '".join(programs)
            marketing_query = f"""
                SELECT 
                    program,
                    channel,
                    fiscal_year,
                    month_date,
                    spend_amount as total_spend
                FROM marketing_spend
                WHERE program IN ('{programs_str}')
                ORDER BY fiscal_year, month_date
            """
            self.marketing_data = pd.read_sql(marketing_query, self.conn)
            
            # Extract month number from month_date
            if not self.marketing_data.empty:
                self.marketing_data['month_date'] = pd.to_datetime(self.marketing_data['month_date'])
                self.marketing_data['month'] = self.marketing_data['month_date'].dt.month
            
            # Load admissions data - pivot from long to wide format
            admissions_query = f"""
                SELECT 
                    program,
                    cohort_year,
                    cohort_season,
                    report_date,
                    metric_name,
                    metric_value
                FROM admissions_metrics
                WHERE program IN ('{programs_str}')
                AND cohort_season = 'fall'
                AND metric_name IN ('inquiries_received', 'total_applications', 'admissions_accepted', 'total_enrolled')
                ORDER BY cohort_year, report_date
            """
            admissions_long = pd.read_sql(admissions_query, self.conn)
            
            if not admissions_long.empty:
                # Convert to datetime and extract month
                admissions_long['report_date'] = pd.to_datetime(admissions_long['report_date'])
                admissions_long['month'] = admissions_long['report_date'].dt.month
                
                # Pivot to wide format
                self.admissions_data = admissions_long.pivot_table(
                    index=['program', 'cohort_year', 'cohort_season', 'month'],
                    columns='metric_name',
                    values='metric_value',
                    aggfunc='max'
                ).reset_index()
            else:
                self.admissions_data = pd.DataFrame()
            
            # Debug logging
            logger.info(f"Loaded {len(self.marketing_data)} marketing records")
            logger.info(f"Loaded {len(self.admissions_data)} admissions records")
            
            if self.marketing_data.empty:
                logger.warning(f"No marketing data found for programs: {programs}")
                return False
            
            if self.admissions_data.empty:
                logger.warning(f"No admissions data found for programs: {programs}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {e}", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def analyze_channel_timing_effectiveness(self, program: str, metric: str) -> pd.DataFrame:
        """
        Analyze channel effectiveness by timing (month)
        
        Args:
            program: Program name
            metric: Target metric (inquiries_received, total_applications, admissions_accepted)
            
        Returns:
            DataFrame with channel-timing effectiveness analysis
        """
        try:
            # Filter data for selected program
            marketing_program = self.marketing_data[self.marketing_data['program'] == program].copy()
            admissions_program = self.admissions_data[self.admissions_data['program'] == program].copy()
            
            if marketing_program.empty or admissions_program.empty:
                return pd.DataFrame()
            
            # Merge marketing and admissions data by month (60-day attribution window)
            results = []
            
            for _, mkt_row in marketing_program.iterrows():
                channel = mkt_row['channel']
                month = mkt_row['month']
                spend = mkt_row['total_spend']
                
                # Find corresponding admissions data (same month or next month for attribution)
                adm_match = admissions_program[
                    (admissions_program['month'] == month) |
                    (admissions_program['month'] == month + 1)
                ]
                
                if not adm_match.empty:
                    # Use average if multiple matches
                    outcomes = adm_match[metric].mean()
                    
                    # Calculate effectiveness metrics
                    efficiency = outcomes / spend if spend > 0 else 0
                    
                    results.append({
                        'channel': channel,
                        'month': month,
                        'total_spend': spend,
                        'attributed_outcomes': outcomes,
                        'spend_efficiency': efficiency
                    })
            
            if not results:
                return pd.DataFrame()
            
            effectiveness_df = pd.DataFrame(results)
            
            # Add month_name column for display
            month_names = {
                1: 'January', 2: 'February', 3: 'March', 4: 'April',
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }
            effectiveness_df['month_name'] = effectiveness_df['month'].map(month_names)
            
            # Calculate consistency score (inverse of coefficient of variation)
            channel_consistency = effectiveness_df.groupby('channel')['spend_efficiency'].agg([
                ('mean_eff', 'mean'),
                ('std_eff', 'std')
            ]).reset_index()
            
            channel_consistency['consistency'] = 1 / (1 + channel_consistency['std_eff'] / (channel_consistency['mean_eff'] + 0.001))
            channel_consistency['consistency'] = channel_consistency['consistency'].fillna(0.5)
            
            # Merge consistency back
            effectiveness_df = effectiveness_df.merge(
                channel_consistency[['channel', 'consistency']], 
                on='channel', 
                how='left'
            )
            
            # Calculate composite effectiveness score (70% efficiency, 30% consistency)
            effectiveness_df['effectiveness_score'] = (
                0.7 * effectiveness_df['spend_efficiency'] / (effectiveness_df['spend_efficiency'].max() + 0.001) +
                0.3 * effectiveness_df['consistency']
            )
            
            return effectiveness_df
            
        except Exception as e:
            logger.error(f"Error analyzing channel timing effectiveness: {e}", exc_info=True)
            return pd.DataFrame()
    
    def forecast_channel_roi(self, channel: str, investment: float, months: int, 
                            effectiveness_data: pd.DataFrame) -> Dict:
        """
        Forecast ROI for a specific channel investment
        
        Args:
            channel: Channel name
            investment: Monthly investment amount
            months: Number of months
            effectiveness_data: Channel effectiveness data
            
        Returns:
            Dict with forecast results
        """
        try:
            channel_data = effectiveness_data[effectiveness_data['channel'] == channel]
            
            if channel_data.empty:
                return {}
            
            # Calculate average efficiency and consistency
            avg_efficiency = channel_data['spend_efficiency'].mean()
            consistency = channel_data['consistency'].iloc[0]
            
            # Forecast outcomes
            monthly_outcomes = investment * avg_efficiency
            total_outcomes = monthly_outcomes * months
            
            # Calculate ROI (outcomes per dollar)
            roi = avg_efficiency
            
            # Confidence based on consistency and data points
            data_points = len(channel_data)
            confidence = min(100, int(consistency * 100 * (data_points / 12)))
            
            # Recommendation based on efficiency
            if avg_efficiency > 0.01:
                recommendation = "Recommended"
                rec_color = "#28a745"
            elif avg_efficiency > 0.005:
                recommendation = "Consider"
                rec_color = "#17a2b8"
            else:
                recommendation = "Caution"
                rec_color = "#ffc107"
            
            return {
                'channel': channel,
                'monthly_forecast': monthly_outcomes,
                'total_forecast': total_outcomes,
                'roi': roi,
                'confidence': confidence,
                'recommendation': recommendation,
                'rec_color': rec_color,
                'avg_efficiency': avg_efficiency,
                'consistency': consistency
            }
            
        except Exception as e:
            logger.error(f"Error forecasting channel ROI: {e}", exc_info=True)
            return {}
    
    def optimize_budget_allocation(self, total_budget: float, months: int,
                                   effectiveness_data: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize budget allocation across channels and months
        
        Args:
            total_budget: Total budget to allocate
            months: Planning period in months
            effectiveness_data: Channel effectiveness data
            
        Returns:
            DataFrame with optimized allocation
        """
        try:
            # Calculate total effectiveness score by channel
            channel_scores = effectiveness_data.groupby('channel').agg({
                'effectiveness_score': 'mean',
                'spend_efficiency': 'mean',
                'consistency': 'first'
            }).reset_index()
            
            # Normalize scores to sum to 1
            total_score = channel_scores['effectiveness_score'].sum()
            channel_scores['allocation_weight'] = channel_scores['effectiveness_score'] / total_score
            
            # Allocate budget proportionally
            channel_scores['allocated_budget'] = channel_scores['allocation_weight'] * total_budget
            
            # Calculate expected outcomes
            channel_scores['expected_outcomes'] = (
                channel_scores['allocated_budget'] * channel_scores['spend_efficiency']
            )
            
            # Calculate ROI
            channel_scores['roi'] = channel_scores['spend_efficiency']
            
            # Sort by effectiveness
            channel_scores = channel_scores.sort_values('effectiveness_score', ascending=False)
            
            return channel_scores
            
        except Exception as e:
            logger.error(f"Error optimizing budget allocation: {e}", exc_info=True)
            return pd.DataFrame()
    
    def get_timing_recommendations(self, effectiveness_data: pd.DataFrame, 
                                  investment: float, months: int) -> List[Dict]:
        """
        Get top timing recommendations for channel investments
        
        Args:
            effectiveness_data: Channel effectiveness data
            investment: Monthly investment amount
            months: Forecast period
            
        Returns:
            List of timing recommendations
        """
        try:
            # Calculate expected outcomes for each channel-month combination
            recommendations = []
            
            for _, row in effectiveness_data.iterrows():
                expected_outcomes = investment * row['spend_efficiency']
                
                # Determine seasonal indicator
                month = row['month']
                if month in [1, 2, 3]:
                    seasonal = "Peak Season"
                    multiplier = 1.2
                elif month in [9, 10]:
                    seasonal = "High Season"
                    multiplier = 1.1
                else:
                    seasonal = ""
                    multiplier = 1.0
                
                adjusted_outcomes = expected_outcomes * multiplier
                
                recommendations.append({
                    'channel': row['channel'],
                    'month': month,
                    'expected_outcomes': adjusted_outcomes,
                    'effectiveness_score': row['effectiveness_score'],
                    'seasonal': seasonal,
                    'recommendation': f"Invest ${investment:,.0f} in {row['channel']} during month {month}"
                })
            
            # Sort by expected outcomes
            recommendations = sorted(recommendations, key=lambda x: x['expected_outcomes'], reverse=True)
            
            return recommendations[:5]  # Top 5
            
        except Exception as e:
            logger.error(f"Error getting timing recommendations: {e}", exc_info=True)
            return []
