"""
Visualization utilities for router performance metrics.
"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from typing import List
from database import RouterMetrics


def create_accuracy_chart(metrics: List[RouterMetrics]) -> str:
    """
    Create a line chart showing accuracy improvement over time.
    Returns base64-encoded PNG image.
    """
    if not metrics:
        # Create empty chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'No data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_title('Router Accuracy Over Time')
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        versions = [m.version for m in metrics]
        accuracies = [m.accuracy * 100 for m in metrics]  # Convert to percentage
        timestamps = [m.timestamp.strftime('%Y-%m-%d %H:%M') for m in metrics]
        
        # Plot accuracy line
        ax.plot(versions, accuracies, marker='o', linewidth=2, markersize=8, 
                color='#2E86AB', label='Accuracy')
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Labels and title
        ax.set_xlabel('Version', fontsize=12, fontweight='bold')
        ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
        ax.set_title('Router Accuracy Improvement Over Time', fontsize=14, fontweight='bold')
        
        # Set y-axis limits
        ax.set_ylim(0, 100)
        
        # Add value labels on points
        for i, (v, a) in enumerate(zip(versions, accuracies)):
            ax.annotate(f'{a:.1f}%', 
                       xy=(v, a), 
                       xytext=(0, 10),
                       textcoords='offset points',
                       ha='center',
                       fontsize=9,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
        
        # Add legend
        ax.legend(loc='lower right')
        
        plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return image_base64


def create_performance_summary_chart(metrics: List[RouterMetrics]) -> str:
    """
    Create a bar chart showing total predictions vs successful predictions.
    Returns base64-encoded PNG image.
    """
    if not metrics:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'No data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_title('Performance Summary')
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        versions = [f'v{m.version}' for m in metrics]
        total_predictions = [m.total_predictions for m in metrics]
        successful_predictions = [m.successful_predictions for m in metrics]
        
        x = range(len(versions))
        width = 0.35
        
        # Create bars
        bars1 = ax.bar([i - width/2 for i in x], total_predictions, width, 
                       label='Total Predictions', color='#A23B72', alpha=0.8)
        bars2 = ax.bar([i + width/2 for i in x], successful_predictions, width, 
                       label='Successful Predictions', color='#F18F01', alpha=0.8)
        
        # Labels and title
        ax.set_xlabel('Version', fontsize=12, fontweight='bold')
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title('Total vs Successful Predictions', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(versions)
        ax.legend()
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return image_base64


def generate_html_report(metrics: List[RouterMetrics]) -> str:
    """
    Generate an HTML report with visualizations.
    """
    accuracy_chart = create_accuracy_chart(metrics)
    performance_chart = create_performance_summary_chart(metrics)
    
    # Calculate statistics
    if metrics:
        latest = metrics[-1]
        initial = metrics[0]
        accuracy_gain = (latest.accuracy - initial.accuracy) * 100
        total_versions = len(metrics)
    else:
        latest = None
        accuracy_gain = 0
        total_versions = 0
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Router Performance Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0 0 10px 0;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .stat-value {{
                font-size: 32px;
                font-weight: bold;
                color: #2E86AB;
                margin: 10px 0;
            }}
            .stat-label {{
                color: #666;
                font-size: 14px;
            }}
            .chart {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            .chart img {{
                max-width: 100%;
                height: auto;
            }}
            .positive {{
                color: #28a745;
            }}
            .negative {{
                color: #dc3545;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 Model Router Performance Report</h1>
            <p>Meta-Learning System Analytics</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Current Accuracy</div>
                <div class="stat-value">{latest.accuracy * 100:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Accuracy Gain</div>
                <div class="stat-value {'positive' if accuracy_gain >= 0 else 'negative'}">
                    {'+' if accuracy_gain >= 0 else ''}{accuracy_gain:.1f}%
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Versions</div>
                <div class="stat-value">{total_versions}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Predictions</div>
                <div class="stat-value">{latest.total_predictions if latest else 0}</div>
            </div>
        </div>
        
        <div class="chart">
            <h2>📈 Accuracy Over Time</h2>
            <img src="data:image/png;base64,{accuracy_chart}" alt="Accuracy Chart">
        </div>
        
        <div class="chart">
            <h2>📊 Performance Summary</h2>
            <img src="data:image/png;base64,{performance_chart}" alt="Performance Chart">
        </div>
    </body>
    </html>
    """
    
    return html
