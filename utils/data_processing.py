"""
Data processing utility functions for Mays Analytics Platform
Functions for generating insights and processing data
"""
import pandas as pd


def generate_insights(current_data, latest_data):
    """Generate automatic insights from the data"""
    insights = []
    
    inquiries = latest_data[latest_data['metric_name'] == 'inquiries_received']['metric_value'].fillna(0).sum()
    applications = latest_data[latest_data['metric_name'] == 'total_applications']['metric_value'].fillna(0).sum()
    offers = latest_data[latest_data['metric_name'] == 'admissions_offered']['metric_value'].fillna(0).sum()
    
    if inquiries > 0 and applications > 0:
        conversion_rate = (applications / inquiries * 100)
        if conversion_rate > 35:
            insights.append(f"🟢 Strong inquiry conversion at {conversion_rate:.1f}% (above 35% benchmark)")
        elif conversion_rate > 25:
            insights.append(f"🟡 Moderate inquiry conversion at {conversion_rate:.1f}% (room for improvement)")
        else:
            insights.append(f"🔴 Low inquiry conversion at {conversion_rate:.1f}% (needs attention)")
    
    if applications > 0 and offers > 0:
        selectivity = (offers / applications * 100)
        if selectivity < 60:
            insights.append(f"🎯 Highly selective program with {selectivity:.1f}% offer rate")
        else:
            insights.append(f"📈 Opportunity to increase selectivity (current: {selectivity:.1f}%)")
    
    program_apps = latest_data[latest_data['metric_name'] == 'total_applications'].groupby('program')['metric_value'].sum()
    if not program_apps.empty:
        top_program = program_apps.idxmax()
        insights.append(f"🏆 {top_program} leads in applications with {int(program_apps.max())} submissions")
    
    return insights
