"""
Attorney Training Simulator Debugger
Focus on gamification and user experience testing
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
from dataclasses import dataclass
import logging

@dataclass
class UserAction:
    timestamp: float
    action_type: str  # 'voice_query', 'click', 'hover', 'scroll'
    target: str
    value: Any
    success: bool
    response_time: float

@dataclass
class TrainingSession:
    session_id: str
    attorney_id: str
    start_time: datetime
    actions: List[UserAction]
    scores: Dict[str, float]
    discoveries: List[str]

class TrainingSimulatorDebugger:
    def __init__(self):
        self.debug_dir = Path("./training_debug")
        self.debug_dir.mkdir(exist_ok=True)
        
        self.sessions = []
        self.current_session = None
        
        # Gamification metrics
        self.achievement_thresholds = {
            'speed_demon': {'query_time': 5.0},  # Under 5 seconds
            'eagle_eye': {'discovery_rate': 0.9},  # 90% discovery
            'pattern_master': {'pattern_recognition': 0.85},
            'efficiency_expert': {'clicks_per_discovery': 3}
        }
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('training_debug.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def start_debug_session(self, attorney_id: str) -> str:
        """Start a new training debug session"""
        session_id = f"session_{int(time.time())}"
        self.current_session = TrainingSession(
            session_id=session_id,
            attorney_id=attorney_id,
            start_time=datetime.now(),
            actions=[],
            scores={},
            discoveries=[]
        )
        
        self.logger.info(f"Started debug session: {session_id}")
        return session_id
    
    def track_action(self, action_type: str, target: str, value: Any, 
                    success: bool, response_time: float):
        """Track user actions for UX analysis"""
        if not self.current_session:
            return
        
        action = UserAction(
            timestamp=time.time(),
            action_type=action_type,
            target=target,
            value=value,
            success=success,
            response_time=response_time
        )
        
        self.current_session.actions.append(action)
        
        # Real-time feedback analysis
        if len(self.current_session.actions) % 10 == 0:
            self.analyze_ux_patterns()
    
    def analyze_ux_patterns(self) -> Dict[str, Any]:
        """Analyze user experience patterns"""
        if not self.current_session:
            return {}
        
        actions = self.current_session.actions
        
        analysis = {
            'total_actions': len(actions),
            'action_types': {},
            'error_rate': 0,
            'avg_response_time': 0,
            'friction_points': [],
            'success_patterns': []
        }
        
        # Action type distribution
        for action in actions:
            analysis['action_types'][action.action_type] = \
                analysis['action_types'].get(action.action_type, 0) + 1
        
        # Error rate
        errors = [a for a in actions if not a.success]
        analysis['error_rate'] = len(errors) / len(actions) if actions else 0
        
        # Response time analysis
        response_times = [a.response_time for a in actions]
        analysis['avg_response_time'] = np.mean(response_times) if response_times else 0
        
        # Identify friction points (repeated failures)
        for i in range(len(actions) - 2):
            if all(not actions[j].success for j in range(i, min(i+3, len(actions)))):
                analysis['friction_points'].append({
                    'timestamp': actions[i].timestamp,
                    'target': actions[i].target,
                    'pattern': 'repeated_failures'
                })
        
        return analysis
    
    def calculate_gamification_scores(self) -> Dict[str, float]:
        """Calculate gamification metrics"""
        if not self.current_session:
            return {}
        
        scores = {
            'query_efficiency': 0,
            'discovery_completeness': 0,
            'pattern_recognition': 0,
            'speed_score': 0,
            'accuracy_score': 0
        }
        
        # Query efficiency (time per discovery)
        discoveries = len(self.current_session.discoveries)
        total_time = sum(a.response_time for a in self.current_session.actions)
        scores['query_efficiency'] = discoveries / total_time if total_time > 0 else 0
        
        # Pattern recognition (successful pattern queries)
        pattern_queries = [a for a in self.current_session.actions 
                          if 'pattern' in a.target.lower()]
        successful_patterns = [a for a in pattern_queries if a.success]
        scores['pattern_recognition'] = \
            len(successful_patterns) / len(pattern_queries) if pattern_queries else 0
        
        # Check achievements
        achievements = self.check_achievements(scores)
        
        return {'scores': scores, 'achievements': achievements}
    
    def check_achievements(self, scores: Dict[str, float]) -> List[str]:
        """Check if user earned any achievements"""
        earned = []
        
        # Implementation would check against thresholds
        # This is simplified for brevity
        
        return earned
    
    def generate_feedback_report(self) -> Dict[str, Any]:
        """Generate comprehensive feedback for attorney"""
        if not self.current_session:
            return {}
        
        ux_analysis = self.analyze_ux_patterns()
        gamification = self.calculate_gamification_scores()
        
        report = {
            'session_id': self.current_session.session_id,
            'duration': (datetime.now() - self.current_session.start_time).seconds,
            'ux_analysis': ux_analysis,
            'gamification': gamification,
            'recommendations': self.generate_recommendations(ux_analysis, gamification)
        }
        
        # Save report
        report_path = self.debug_dir / f"{self.current_session.session_id}_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def generate_recommendations(self, ux_analysis: Dict, gamification: Dict) -> List[str]:
        """Generate personalized training recommendations"""
        recommendations = []
        
        if ux_analysis['error_rate'] > 0.2:
            recommendations.append("Practice basic query syntax - error rate is high")
        
        if ux_analysis['avg_response_time'] > 10:
            recommendations.append("Focus on query optimization for faster results")
        
        if gamification['scores']['pattern_recognition'] < 0.7:
            recommendations.append("Review financial pattern detection tutorials")
        
        return recommendations
