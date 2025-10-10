#!/usr/bin/env python3
"""
Test suite for Feedback Loop automation and tiered training system
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required classes
from main import MLModels, FeedbackLoop, DataFetcher, TechnicalIndicators


class TestMLModelsPerformanceTracking(unittest.TestCase):
    """Test MLModels performance tracking features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ml_models = MLModels()
    
    def test_initialization(self):
        """Test that MLModels initializes with performance tracking"""
        self.assertIsInstance(self.ml_models.performance_history, list)
        self.assertIsInstance(self.ml_models.model_versions, dict)
        self.assertEqual(len(self.ml_models.performance_history), 0)
    
    def test_save_performance_metrics(self):
        """Test saving performance metrics"""
        metrics = {'accuracy': 0.75, 'precision': 0.72}
        self.ml_models.save_performance_metrics('test_model', metrics)
        
        self.assertEqual(len(self.ml_models.performance_history), 1)
        record = self.ml_models.performance_history[0]
        self.assertEqual(record['model_name'], 'test_model')
        self.assertEqual(record['metrics'], metrics)
        self.assertIsInstance(record['timestamp'], datetime)
    
    def test_get_performance_trend_insufficient_data(self):
        """Test performance trend with insufficient data"""
        trend = self.ml_models.get_performance_trend('test_model')
        self.assertEqual(trend['trend'], 'insufficient_data')
        self.assertEqual(trend['improvement'], 0.0)
    
    def test_get_performance_trend_improving(self):
        """Test performance trend detection - improving"""
        # Add multiple performance records with improving accuracy
        for i in range(5):
            metrics = {'accuracy': 0.6 + i * 0.05}
            self.ml_models.save_performance_metrics('test_model', metrics)
        
        trend = self.ml_models.get_performance_trend('test_model')
        self.assertEqual(trend['trend'], 'improving')
        self.assertGreater(trend['improvement'], 0)
    
    def test_get_performance_trend_degrading(self):
        """Test performance trend detection - degrading"""
        # Add multiple performance records with degrading accuracy
        for i in range(5):
            metrics = {'accuracy': 0.8 - i * 0.05}
            self.ml_models.save_performance_metrics('test_model', metrics)
        
        trend = self.ml_models.get_performance_trend('test_model')
        self.assertEqual(trend['trend'], 'degrading')
        self.assertLess(trend['improvement'], 0)


class TestFeedbackLoop(unittest.TestCase):
    """Test FeedbackLoop class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ml_models = MLModels()
        self.data_fetcher = DataFetcher()
        self.feedback_loop = FeedbackLoop(self.ml_models, self.data_fetcher)
    
    def test_initialization(self):
        """Test FeedbackLoop initialization"""
        self.assertIsNotNone(self.feedback_loop.ml_models)
        self.assertIsNotNone(self.feedback_loop.data_fetcher)
        self.assertIsInstance(self.feedback_loop.config, dict)
        self.assertIsInstance(self.feedback_loop.prediction_log, list)
        self.assertFalse(self.feedback_loop.training_in_progress)
    
    def test_config_default_values(self):
        """Test default configuration values"""
        config = self.feedback_loop.config
        self.assertIn('tier1_interval', config)
        self.assertIn('tier2_interval', config)
        self.assertIn('tier3_interval', config)
        self.assertIn('performance_threshold', config)
        self.assertGreater(config['tier1_interval'], 0)
        self.assertLess(config['tier1_interval'], config['tier2_interval'])
        self.assertLess(config['tier2_interval'], config['tier3_interval'])
    
    def test_log_prediction_outcome(self):
        """Test logging prediction outcomes"""
        prediction = {'signal': 'BUY', 'ensemble': 0.7}
        actual_outcome = 'BUY'
        
        self.feedback_loop.log_prediction_outcome(prediction, actual_outcome)
        
        self.assertEqual(len(self.feedback_loop.prediction_log), 1)
        record = self.feedback_loop.prediction_log[0]
        self.assertEqual(record['prediction'], prediction)
        self.assertEqual(record['actual'], actual_outcome)
        self.assertTrue(record['correct'])
    
    def test_log_prediction_outcome_incorrect(self):
        """Test logging incorrect prediction"""
        prediction = {'signal': 'BUY', 'ensemble': 0.7}
        actual_outcome = 'SELL'
        
        self.feedback_loop.log_prediction_outcome(prediction, actual_outcome)
        
        record = self.feedback_loop.prediction_log[0]
        self.assertFalse(record['correct'])
    
    def test_prediction_log_size_limit(self):
        """Test that prediction log doesn't grow unbounded"""
        # Add more than 1000 predictions
        for i in range(1100):
            prediction = {'signal': 'BUY', 'ensemble': 0.7}
            self.feedback_loop.log_prediction_outcome(prediction, 'BUY')
        
        # Should be limited to 1000
        self.assertEqual(len(self.feedback_loop.prediction_log), 1000)
    
    def test_calculate_recent_performance_insufficient_data(self):
        """Test performance calculation with insufficient data"""
        perf = self.feedback_loop.calculate_recent_performance()
        self.assertEqual(perf['accuracy'], 0.0)
        self.assertLess(perf['total_predictions'], self.feedback_loop.config['evaluation_window'])
    
    def test_calculate_recent_performance_with_data(self):
        """Test performance calculation with sufficient data"""
        # Add predictions with 70% accuracy
        for i in range(15):
            prediction = {'signal': 'BUY', 'ensemble': 0.7}
            actual = 'BUY' if i < 10 else 'SELL'  # 10 correct, 5 incorrect
            self.feedback_loop.log_prediction_outcome(prediction, actual)
        
        perf = self.feedback_loop.calculate_recent_performance()
        self.assertGreater(perf['accuracy'], 0)
        self.assertEqual(perf['total_predictions'], self.feedback_loop.config['evaluation_window'])
    
    def test_should_retrain_never_trained(self):
        """Test that retraining is triggered when never trained"""
        should_train = self.feedback_loop.should_retrain('tier1')
        self.assertTrue(should_train)
    
    def test_should_retrain_training_in_progress(self):
        """Test that retraining is blocked when training in progress"""
        self.feedback_loop.training_in_progress = True
        should_train = self.feedback_loop.should_retrain('tier1')
        self.assertFalse(should_train)
    
    def test_should_retrain_time_based(self):
        """Test time-based retraining trigger"""
        # Set last training to more than tier1_interval ago
        self.feedback_loop.last_training['tier1'] = (
            datetime.now() - timedelta(seconds=self.feedback_loop.config['tier1_interval'] + 100)
        )
        
        should_train = self.feedback_loop.should_retrain('tier1')
        self.assertTrue(should_train)
    
    def test_should_retrain_performance_based(self):
        """Test performance-based retraining trigger"""
        # Set recent training time
        self.feedback_loop.last_training['tier1'] = datetime.now()
        
        # Add predictions with poor performance
        for i in range(15):
            prediction = {'signal': 'BUY', 'ensemble': 0.7}
            actual = 'SELL'  # All incorrect
            self.feedback_loop.log_prediction_outcome(prediction, actual)
        
        should_train = self.feedback_loop.should_retrain('tier1')
        self.assertTrue(should_train)
    
    def test_get_feedback_loop_status(self):
        """Test getting feedback loop status"""
        status = self.feedback_loop.get_feedback_loop_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('training_in_progress', status)
        self.assertIn('recent_performance', status)
        self.assertIn('prediction_log_size', status)
        self.assertIn('last_training', status)
        self.assertIn('config', status)
        self.assertIn('model_performance_trends', status)
    
    def test_tier_training_methods_exist(self):
        """Test that all tier training methods exist"""
        self.assertTrue(hasattr(self.feedback_loop, 'tier1_training'))
        self.assertTrue(hasattr(self.feedback_loop, 'tier2_training'))
        self.assertTrue(hasattr(self.feedback_loop, 'tier3_training'))
        self.assertTrue(callable(self.feedback_loop.tier1_training))
        self.assertTrue(callable(self.feedback_loop.tier2_training))
        self.assertTrue(callable(self.feedback_loop.tier3_training))


class TestTieredTrainingSystem(unittest.TestCase):
    """Test the tiered training system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ml_models = MLModels()
        self.data_fetcher = DataFetcher()
        self.feedback_loop = FeedbackLoop(self.ml_models, self.data_fetcher)
        
        # Create sample data for training
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 40000 + np.cumsum(np.random.randn(100) * 100)
        self.sample_df = pd.DataFrame({
            'price': prices,
            'volume': np.random.randint(1000, 10000, 100),
            'market_cap': prices * np.random.randint(1000000, 2000000, 100)
        }, index=dates)
        
        # Add some technical indicators
        indicators = TechnicalIndicators()
        self.sample_df = indicators.add_all_indicators(self.sample_df)
    
    def test_tier1_training_returns_results(self):
        """Test that Tier 1 training returns results"""
        result = self.feedback_loop.tier1_training(self.sample_df)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['tier'], 'tier1')
        self.assertIn('logistic_accuracy', result)
    
    def test_tier2_training_returns_results(self):
        """Test that Tier 2 training returns results"""
        result = self.feedback_loop.tier2_training(self.sample_df)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['tier'], 'tier2')
        self.assertIn('logistic_accuracy', result)
        self.assertIn('xgboost_accuracy', result)
    
    def test_tier3_training_returns_results(self):
        """Test that Tier 3 training returns results"""
        result = self.feedback_loop.tier3_training(self.sample_df)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['tier'], 'tier3')
        self.assertIn('logistic_accuracy', result)
        self.assertIn('xgboost_accuracy', result)
        self.assertIn('lstm_accuracy', result)
    
    def test_tier_training_updates_timestamps(self):
        """Test that training updates last_training timestamps"""
        self.assertIsNone(self.feedback_loop.last_training['tier1'])
        
        self.feedback_loop.tier1_training(self.sample_df)
        
        self.assertIsNotNone(self.feedback_loop.last_training['tier1'])
        self.assertIsInstance(self.feedback_loop.last_training['tier1'], datetime)
    
    def test_tier_training_saves_metrics(self):
        """Test that training saves performance metrics"""
        initial_count = len(self.ml_models.performance_history)
        
        self.feedback_loop.tier1_training(self.sample_df)
        
        self.assertGreater(len(self.ml_models.performance_history), initial_count)


def main():
    """Run all tests"""
    print("=" * 60)
    print("Feedback Loop and Tiered Training System Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMLModelsPerformanceTracking))
    suite.addTests(loader.loadTestsFromTestCase(TestFeedbackLoop))
    suite.addTests(loader.loadTestsFromTestCase(TestTieredTrainingSystem))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {len(result.failures) + len(result.errors)} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
