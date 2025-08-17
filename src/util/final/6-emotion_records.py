#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyze emotion records from app_analysis_final.json
and create a pie chart visualization showing the distribution of 8 emotion types.
"""

import json
import matplotlib.pyplot as plt
import os
from collections import Counter

# Set up Korean font support for matplotlib
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_emotion_records(file_path):
    """Load emotion records from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('emotion_records', [])

def analyze_emotions(emotion_records):
    """Count occurrences of each emotion type"""
    emotion_counts = Counter()
    
    for record in emotion_records:
        emotion = record.get('emotion', '')
        if emotion:
            emotion_counts[emotion] += 1
    
    return emotion_counts

def create_pie_chart(emotion_counts, output_path):
    """Create a pie chart showing emotion distribution"""
    
    # Sort emotions by count (descending)
    sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
    emotions = [item[0] for item in sorted_emotions]
    counts = [item[1] for item in sorted_emotions]
    
    # Define colors for each emotion - blue for positive, red for negative
    emotion_colors = {
        # Positive emotions (blue-type colors)
        '차분해요': '#4169E1',      # Royal blue (calm)
        '행복해요': '#1E90FF',      # Dodger blue (happy)
        '만족스러워요': '#6495ED',  # Cornflower blue (satisfied)
        '신나요': '#87CEEB',        # Sky blue (excited)
        # Negative emotions (red-type colors)
        '우울해요': '#DC143C',      # Crimson (depressed)
        '슬퍼요': '#B22222',        # Fire brick (sad)
        '화가나요': '#FF0000',      # Red (angry)
        '불안해요': '#CD5C5C'       # Indian red (anxious)
    }
    
    colors = [emotion_colors.get(emotion, '#808080') for emotion in emotions]
    
    # Create figure and axis
    plt.figure(figsize=(12, 10))
    
    # Create pie chart
    wedges, texts, autotexts = plt.pie(
        counts, 
        labels=emotions, 
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )
    
    # Customize the chart
    plt.title('감정 기록 분포\n(8가지 감정 유형)', 
             fontsize=16, fontweight='bold', pad=20)
    
    # Add count information to labels
    for i, (emotion, count) in enumerate(zip(emotions, counts)):
        total_records = sum(counts)
        texts[i].set_text(f'{emotion}\n({count:,}개)')
    
    # Equal aspect ratio ensures pie chart is circular
    plt.axis('equal')
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the chart
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Pie chart saved to: {output_path}")

def main():
    """Main function to run the emotion analysis"""
    
    # File paths
    input_file = "data/figures/final/app_analysis_final.json"
    output_file = "data/figures/final/6-감정별_비율_원그래프.png"
    
    try:
        # Load emotion data
        print("Loading emotion records...")
        emotion_records = load_emotion_records(input_file)
        print(f"Loaded {len(emotion_records):,} emotion records")
        
        # Analyze emotions
        print("Analyzing emotions...")
        emotion_counts = analyze_emotions(emotion_records)
        
        total_records = sum(emotion_counts.values())
        print(f"\nEmotion Analysis Results:")
        print(f"Total emotion records: {total_records:,}")
        print(f"Number of emotion types: {len(emotion_counts)}")
        
        print("\nEmotion breakdown:")
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total_records * 100
            print(f"  {emotion}: {count:,} ({percentage:.1f}%)")
        
        # Create pie chart
        print(f"\nCreating pie chart...")
        create_pie_chart(emotion_counts, output_file)
        
        print("Emotion analysis completed successfully!")
        
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    main()