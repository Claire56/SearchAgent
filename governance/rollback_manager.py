"""Rollback manager for agent state management."""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.config import config
from utils.logger import logger


class RollbackManager:
    """Manages agent state snapshots and rollbacks."""
    
    def __init__(self, state_dir: Optional[str] = None):
        self.enabled = config.enable_rollback
        self.state_dir = Path(state_dir or config.state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints: List[str] = []
    
    def create_checkpoint(self, state: Dict[str, Any], checkpoint_id: Optional[str] = None) -> str:
        """
        Create a state checkpoint.
        
        Args:
            state: Agent state dictionary
            checkpoint_id: Optional checkpoint ID (auto-generated if not provided)
        
        Returns:
            Checkpoint ID
        """
        if not self.enabled:
            return ""
        
        import uuid
        if checkpoint_id is None:
            checkpoint_id = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        checkpoint_file = self.state_dir / f"{checkpoint_id}.json"
        
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "state": state
        }
        
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint_data, f, indent=2)
            
            self.checkpoints.append(checkpoint_id)
            logger.info(f"Checkpoint created: {checkpoint_id}")
            
            return checkpoint_id
        
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return ""
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint ID
        
        Returns:
            State dictionary or None if not found
        """
        checkpoint_file = self.state_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            logger.warning(f"Checkpoint not found: {checkpoint_id}")
            return None
        
        try:
            with open(checkpoint_file, "r") as f:
                checkpoint_data = json.load(f)
            
            logger.info(f"Checkpoint loaded: {checkpoint_id}")
            return checkpoint_data.get("state")
        
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None
    
    def rollback(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Rollback to a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint ID to rollback to
        
        Returns:
            Rolled back state or None if failed
        """
        logger.warning(f"Rolling back to checkpoint: {checkpoint_id}")
        
        state = self.load_checkpoint(checkpoint_id)
        
        if state:
            logger.info(f"Successfully rolled back to checkpoint: {checkpoint_id}")
        else:
            logger.error(f"Failed to rollback to checkpoint: {checkpoint_id}")
        
        return state
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available checkpoints."""
        checkpoints = []
        
        for checkpoint_file in self.state_dir.glob("checkpoint_*.json"):
            try:
                with open(checkpoint_file, "r") as f:
                    checkpoint_data = json.load(f)
                    checkpoints.append({
                        "checkpoint_id": checkpoint_data.get("checkpoint_id"),
                        "timestamp": checkpoint_data.get("timestamp"),
                        "file": str(checkpoint_file)
                    })
            except Exception:
                pass
        
        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return checkpoints
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint."""
        checkpoint_file = self.state_dir / f"{checkpoint_id}.json"
        
        if checkpoint_file.exists():
            try:
                checkpoint_file.unlink()
                if checkpoint_id in self.checkpoints:
                    self.checkpoints.remove(checkpoint_id)
                logger.info(f"Checkpoint deleted: {checkpoint_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete checkpoint: {e}")
                return False
        
        return False
