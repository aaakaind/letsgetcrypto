"""
ML Model versioning and persistence utilities for LetsGetCrypto.

Provides improved model serialization, versioning, and metadata tracking.
"""

import hashlib
import json
import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class ModelVersion:
    """Model version information"""
    
    def __init__(self, 
                 model_type: str,
                 version: str,
                 created_at: datetime,
                 metrics: Optional[Dict[str, float]] = None,
                 hyperparameters: Optional[Dict[str, Any]] = None,
                 training_data_hash: Optional[str] = None):
        """
        Initialize model version
        
        Args:
            model_type: Type of model (e.g., 'lstm', 'xgboost', 'logistic_regression')
            version: Version string (e.g., 'v1.0.0')
            created_at: Creation timestamp
            metrics: Performance metrics (accuracy, loss, etc.)
            hyperparameters: Model hyperparameters
            training_data_hash: Hash of training data for reproducibility
        """
        self.model_type = model_type
        self.version = version
        self.created_at = created_at
        self.metrics = metrics or {}
        self.hyperparameters = hyperparameters or {}
        self.training_data_hash = training_data_hash
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'model_type': self.model_type,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'metrics': self.metrics,
            'hyperparameters': self.hyperparameters,
            'training_data_hash': self.training_data_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelVersion':
        """Create from dictionary"""
        return cls(
            model_type=data['model_type'],
            version=data['version'],
            created_at=datetime.fromisoformat(data['created_at']),
            metrics=data.get('metrics'),
            hyperparameters=data.get('hyperparameters'),
            training_data_hash=data.get('training_data_hash')
        )


class ModelManager:
    """Manager for ML model persistence and versioning"""
    
    def __init__(self, models_dir: Union[str, Path] = 'model_weights'):
        """
        Initialize model manager
        
        Args:
            models_dir: Directory to store model files
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.models_dir / 'metadata.json'
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load model metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
                return {'models': {}}
        return {'models': {}}
    
    def _save_metadata(self) -> None:
        """Save model metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _get_model_path(self, model_type: str, version: str, 
                       extension: str = '.pkl') -> Path:
        """Get path for model file"""
        return self.models_dir / f"{model_type}_{version}{extension}"
    
    def _calculate_data_hash(self, data: Any) -> Optional[str]:
        """
        Calculate hash of training data for reproducibility.
        
        Returns:
            str: 16-character hash string if hash can be computed.
            None: If NumPy is not available and hash cannot be computed.
        """
        if not NUMPY_AVAILABLE:
            logger.warning("NumPy not available, cannot calculate data hash")
            return None
        
        if hasattr(data, 'tobytes'):
            return hashlib.sha256(data.tobytes()).hexdigest()[:16]
        else:
            # Fallback for non-numpy data
            return hashlib.sha256(str(data).encode()).hexdigest()[:16]
    
    def save_model(self,
                   model: Any,
                   model_type: str,
                   version: Optional[str] = None,
                   metrics: Optional[Dict[str, float]] = None,
                   hyperparameters: Optional[Dict[str, Any]] = None,
                   training_data: Optional[Any] = None) -> str:
        """
        Save model with versioning and metadata
        
        Args:
            model: Model object to save
            model_type: Type of model
            version: Version string (auto-generated if not provided)
            metrics: Performance metrics
            hyperparameters: Model hyperparameters
            training_data: Training data for hash calculation (numpy array or other)
        
        Returns:
            Version string
        """
        # Generate version if not provided
        if version is None:
            version = datetime.now().strftime('v%Y%m%d_%H%M%S')
        
        # Calculate training data hash
        data_hash = None
        if training_data is not None:
            data_hash = self._calculate_data_hash(training_data)
        
        # Create model version
        model_version = ModelVersion(
            model_type=model_type,
            version=version,
            created_at=datetime.now(),
            metrics=metrics,
            hyperparameters=hyperparameters,
            training_data_hash=data_hash
        )
        
        # Determine file extension based on model type
        extension = '.pkl'
        if hasattr(model, 'save'):  # Keras/TensorFlow models
            extension = '.h5'
        
        # Save model
        model_path = self._get_model_path(model_type, version, extension)
        
        try:
            if extension == '.h5':
                # TensorFlow/Keras model
                model.save(str(model_path))
            else:
                # Scikit-learn or other pickle-able models
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Update metadata
            model_key = f"{model_type}_{version}"
            self.metadata['models'][model_key] = model_version.to_dict()
            self._save_metadata()
            
            logger.info(f"Saved model {model_type} version {version} to {model_path}")
            return version
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    def load_model(self,
                   model_type: str,
                   version: Optional[str] = None) -> Tuple[Any, ModelVersion]:
        """
        Load model with metadata
        
        Args:
            model_type: Type of model to load
            version: Specific version to load (latest if not provided)
        
        Returns:
            Tuple of (model, model_version)
        
        Raises:
            FileNotFoundError: If model not found
        """
        # Get version
        if version is None:
            version = self.get_latest_version(model_type)
            if version is None:
                raise FileNotFoundError(f"No saved models found for {model_type}")
        
        # Get model metadata
        model_key = f"{model_type}_{version}"
        if model_key not in self.metadata['models']:
            raise FileNotFoundError(f"Model {model_key} not found in metadata")
        
        model_version = ModelVersion.from_dict(self.metadata['models'][model_key])
        
        # Try different extensions
        for extension in ['.pkl', '.h5']:
            model_path = self._get_model_path(model_type, version, extension)
            
            if model_path.exists():
                try:
                    if extension == '.h5':
                        # TensorFlow/Keras model
                        try:
                            from tensorflow import keras
                            model = keras.models.load_model(str(model_path))
                        except ImportError:
                            logger.error("TensorFlow not available, cannot load HDF5 model")
                            continue
                    else:
                        # Pickle model
                        with open(model_path, 'rb') as f:
                            model = pickle.load(f)
                    
                    logger.info(f"Loaded model {model_type} version {version} from {model_path}")
                    return model, model_version
                    
                except Exception as e:
                    logger.error(f"Failed to load model from {model_path}: {e}")
                    continue
        
        raise FileNotFoundError(f"Model file not found for {model_key}")
    
    def get_latest_version(self, model_type: str) -> Optional[str]:
        """
        Get latest version for a model type
        
        Args:
            model_type: Type of model
        
        Returns:
            Latest version string or None if no versions exist
        """
        versions = []
        for key, data in self.metadata['models'].items():
            if data['model_type'] == model_type:
                versions.append((data['created_at'], data['version']))
        
        if not versions:
            return None
        
        # Sort by creation time and return latest
        versions.sort(reverse=True)
        return versions[0][1]
    
    def list_versions(self, model_type: Optional[str] = None) -> List[ModelVersion]:
        """
        List all model versions
        
        Args:
            model_type: Filter by model type (all if None)
        
        Returns:
            List of ModelVersion objects
        """
        versions = []
        for key, data in self.metadata['models'].items():
            if model_type is None or data['model_type'] == model_type:
                versions.append(ModelVersion.from_dict(data))
        
        # Sort by creation time (newest first)
        versions.sort(key=lambda v: v.created_at, reverse=True)
        return versions
    
    def delete_version(self, model_type: str, version: str) -> bool:
        """
        Delete a specific model version
        
        Args:
            model_type: Type of model
            version: Version to delete
        
        Returns:
            True if deleted successfully
        """
        model_key = f"{model_type}_{version}"
        
        if model_key not in self.metadata['models']:
            logger.warning(f"Model {model_key} not found in metadata")
            return False
        
        # Delete model files
        deleted = False
        for extension in ['.pkl', '.h5']:
            model_path = self._get_model_path(model_type, version, extension)
            if model_path.exists():
                try:
                    model_path.unlink()
                    deleted = True
                    logger.info(f"Deleted model file: {model_path}")
                except Exception as e:
                    logger.error(f"Failed to delete {model_path}: {e}")
        
        # Remove from metadata
        del self.metadata['models'][model_key]
        self._save_metadata()
        
        return deleted
    
    def get_model_info(self, model_type: str, version: str) -> Optional[ModelVersion]:
        """
        Get information about a specific model version
        
        Args:
            model_type: Type of model
            version: Version string
        
        Returns:
            ModelVersion object or None if not found
        """
        model_key = f"{model_type}_{version}"
        
        if model_key in self.metadata['models']:
            return ModelVersion.from_dict(self.metadata['models'][model_key])
        
        return None
    
    def cleanup_old_versions(self, model_type: str, keep_latest: int = 5) -> int:
        """
        Clean up old model versions, keeping only the latest N
        
        Args:
            model_type: Type of model
            keep_latest: Number of latest versions to keep
        
        Returns:
            Number of versions deleted
        """
        versions = self.list_versions(model_type)
        
        if len(versions) <= keep_latest:
            return 0
        
        # Delete old versions
        deleted_count = 0
        for version_info in versions[keep_latest:]:
            if self.delete_version(version_info.model_type, version_info.version):
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old versions of {model_type}")
        return deleted_count
