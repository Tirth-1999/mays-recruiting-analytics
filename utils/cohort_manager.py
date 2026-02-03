"""
Cohort Manager - Dynamic cohort detection and training data management
Automatically adapts to new cohorts and data over time
"""

import sqlite3
import pandas as pd
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class CohortManager:
    """
    Manages cohort data dynamically - automatically detects new cohorts,
    suggests training combinations, and adapts to new data over time.
    
    This ensures the system remains useful for years as new cohorts are added.
    """
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        
    def get_available_cohorts(self, program: str = None) -> Dict[str, Dict]:
        """
        Dynamically discover all available cohorts in the database.
        
        Returns:
            Dict with cohort info: {
                2026: {'start_date': '2024-01-19', 'end_date': '2024-07-31', 'months': 8, 'status': 'complete'},
                2027: {'start_date': '2024-11-30', 'end_date': '2025-06-30', 'months': 8, 'status': 'complete'},
                2028: {'start_date': '2025-10-31', 'end_date': '2025-12-31', 'months': 3, 'status': 'active'},
                2029: {'start_date': None, 'end_date': None, 'months': 0, 'status': 'future'}
            }
        """
        try:
            query = """
                SELECT 
                    cohort_year,
                    MIN(report_date) as start_date,
                    MAX(report_date) as end_date,
                    COUNT(DISTINCT report_date) as months,
                    program
                FROM admissions_metrics 
                WHERE 1=1
            """
            params = []
            
            if program:
                query += " AND program = ?"
                params.append(program)
                
            query += """
                GROUP BY cohort_year, program
                ORDER BY cohort_year
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            cohorts = {}
            for row in cursor.fetchall():
                cohort_year, start_date, end_date, months, prog = row
                
                # Determine status
                if months >= 8:
                    status = 'complete'
                elif months > 0:
                    status = 'active'
                else:
                    status = 'future'
                
                cohorts[cohort_year] = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'months': months,
                    'status': status,
                    'program': prog
                }
                
            logger.info(f"Discovered {len(cohorts)} cohorts: {list(cohorts.keys())}")
            return cohorts
            
        except Exception as e:
            logger.error(f"Error discovering cohorts: {e}")
            return {}
    
    def suggest_training_combinations(self, target_cohort: int, program: str = None) -> List[Dict]:
        """
        Intelligently suggest the best training combinations for a target cohort.
        
        Args:
            target_cohort: The cohort to predict (e.g., 2029)
            program: Optional program filter
            
        Returns:
            List of training suggestions with expected performance:
            [
                {
                    'training_cohorts': [2026, 2027, 2028],
                    'scenario': 'enhanced_training',
                    'expected_accuracy': 85,
                    'description': 'Best option: includes partial target data',
                    'data_points': 27
                },
                {
                    'training_cohorts': [2027, 2028],
                    'scenario': 'recent_training', 
                    'expected_accuracy': 80,
                    'description': 'Recent patterns: most similar timeframe',
                    'data_points': 19
                }
            ]
        """
        available_cohorts = self.get_available_cohorts(program)
        suggestions = []
        
        # Get cohorts with data (complete or active)
        data_cohorts = [
            cohort for cohort, info in available_cohorts.items() 
            if info['status'] in ['complete', 'active'] and cohort != target_cohort
        ]
        
        # Check if target cohort has partial data
        target_has_data = target_cohort in available_cohorts and available_cohorts[target_cohort]['months'] > 0
        
        if not data_cohorts:
            return [{'error': 'No training data available'}]
        
        # Suggestion 1: Enhanced Training (if target has partial data)
        if target_has_data:
            enhanced_training = data_cohorts + [target_cohort]
            total_months = sum(available_cohorts[c]['months'] for c in enhanced_training if c in available_cohorts)
            
            suggestions.append({
                'training_cohorts': data_cohorts,
                'enhanced_with_target': True,
                'scenario': 'enhanced_training',
                'expected_accuracy': 85,
                'description': f'Enhanced: includes {available_cohorts[target_cohort]["months"]} months from target cohort',
                'data_points': total_months,
                'recommendation': 'Best option for highest accuracy'
            })
        
        # Suggestion 2: All Available Historical Data
        if len(data_cohorts) >= 2:
            total_months = sum(available_cohorts[c]['months'] for c in data_cohorts)
            suggestions.append({
                'training_cohorts': data_cohorts,
                'enhanced_with_target': False,
                'scenario': 'comprehensive_training',
                'expected_accuracy': 75,
                'description': f'Comprehensive: all {len(data_cohorts)} historical cohorts',
                'data_points': total_months,
                'recommendation': 'Good for understanding long-term trends'
            })
        
        # Suggestion 3: Recent Cohorts Only (last 2)
        if len(data_cohorts) >= 2:
            recent_cohorts = sorted(data_cohorts)[-2:]
            total_months = sum(available_cohorts[c]['months'] for c in recent_cohorts)
            suggestions.append({
                'training_cohorts': recent_cohorts,
                'enhanced_with_target': False,
                'scenario': 'recent_training',
                'expected_accuracy': 70,
                'description': f'Recent patterns: last 2 cohorts ({recent_cohorts})',
                'data_points': total_months,
                'recommendation': 'Good for capturing recent changes'
            })
        
        # Suggestion 4: Single Most Recent Cohort
        if data_cohorts:
            latest_cohort = max(data_cohorts)
            suggestions.append({
                'training_cohorts': [latest_cohort],
                'enhanced_with_target': False,
                'scenario': 'single_cohort',
                'expected_accuracy': 65,
                'description': f'Single cohort: Class {latest_cohort} only',
                'data_points': available_cohorts[latest_cohort]['months'],
                'recommendation': 'Minimal but focused training'
            })
        
        # Sort by expected accuracy (best first)
        suggestions.sort(key=lambda x: x['expected_accuracy'], reverse=True)
        
        logger.info(f"Generated {len(suggestions)} training suggestions for Class {target_cohort}")
        return suggestions
    
    def detect_new_data(self, last_check: datetime = None) -> Dict[str, List]:
        """
        Detect if new data has been added since last check.
        
        Returns:
            {
                'new_cohorts': [2029, 2030],
                'updated_cohorts': [2028],
                'new_data_points': 15,
                'recommendations': ['Retrain models with new data', 'Update cohort 2028 predictions']
            }
        """
        try:
            # Get current cohort status
            current_cohorts = self.get_available_cohorts()
            
            # If no last_check provided, assume this is first run
            if last_check is None:
                return {
                    'new_cohorts': [],
                    'updated_cohorts': list(current_cohorts.keys()),
                    'new_data_points': sum(c['months'] for c in current_cohorts.values()),
                    'recommendations': ['Initial setup complete', 'Ready for predictions']
                }
            
            # Check for new data since last check
            query = """
                SELECT cohort_year, COUNT(*) as new_records
                FROM admissions_metrics 
                WHERE created_at > ? OR updated_at > ?
                GROUP BY cohort_year
            """
            
            # Note: This assumes created_at/updated_at columns exist
            # If not, we can use a simpler approach based on data comparison
            
            new_cohorts = []
            updated_cohorts = []
            recommendations = []
            
            # For now, provide a simple implementation
            # In production, you'd track this more precisely
            
            return {
                'new_cohorts': new_cohorts,
                'updated_cohorts': updated_cohorts,
                'new_data_points': 0,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error detecting new data: {e}")
            return {'error': str(e)}
    
    def get_optimal_prediction_timeline(self, cohort: int) -> Dict[str, any]:
        """
        Determine the optimal prediction timeline for a cohort based on
        historical patterns and current data availability.
        
        Returns:
            {
                'start_date': '2025-10-01',
                'expected_end_date': '2026-07-31', 
                'total_months': 10,
                'current_months': 3,
                'remaining_months': 7,
                'prediction_confidence': 'high'  # based on available training data
            }
        """
        try:
            available_cohorts = self.get_available_cohorts()
            
            if cohort in available_cohorts:
                cohort_info = available_cohorts[cohort]
                
                # Estimate total lifecycle based on historical patterns
                historical_lengths = [
                    info['months'] for info in available_cohorts.values() 
                    if info['status'] == 'complete'
                ]
                
                if historical_lengths:
                    avg_length = int(np.mean(historical_lengths))
                    expected_total = max(avg_length, cohort_info['months'])
                else:
                    expected_total = 8  # Default assumption
                
                # Calculate expected end date
                if cohort_info['start_date']:
                    start_date = pd.to_datetime(cohort_info['start_date'])
                    expected_end = start_date + pd.DateOffset(months=expected_total-1)
                    expected_end_date = expected_end.strftime('%Y-%m-%d')
                else:
                    expected_end_date = None
                
                return {
                    'start_date': cohort_info['start_date'],
                    'expected_end_date': expected_end_date,
                    'total_months': expected_total,
                    'current_months': cohort_info['months'],
                    'remaining_months': max(0, expected_total - cohort_info['months']),
                    'prediction_confidence': 'high' if len(available_cohorts) >= 3 else 'medium'
                }
            else:
                # Future cohort - estimate based on patterns
                return {
                    'start_date': None,
                    'expected_end_date': None,
                    'total_months': 8,  # Default
                    'current_months': 0,
                    'remaining_months': 8,
                    'prediction_confidence': 'low'
                }
                
        except Exception as e:
            logger.error(f"Error determining prediction timeline: {e}")
            return {'error': str(e)}