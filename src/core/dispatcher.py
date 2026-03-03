"""
Dispatcher - Dual-mode dispatcher managing A/B/C modes

Modes:
- A (human relay): Human makes decisions, AI assists
- B (auto): Fully automated AI generation
- C (mixed): AI generates draft, human reviews and edits
"""

import logging
from enum import Enum
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class DispatchMode(Enum):
    """Dispatch mode enumeration"""
    HUMAN_RELAY = "A"      # Human makes decisions, AI assists
    AUTO = "B"             # Fully automated AI generation
    MIXED = "C"            # AI generates draft, human reviews
    

class Dispatcher:
    """Manages dual-mode dispatch for step execution"""
    
    def __init__(self, gemini_client, mode: str = "C"):
        """
        Initialize Dispatcher
        
        Args:
            gemini_client: Gemini API client
            mode: Default execution mode (A, B, or C)
        """
        self.gemini_client = gemini_client
        self.mode = DispatchMode(mode)
        logger.info(f"Dispatcher initialized with mode: {self.mode.value}")
    
    def set_mode(self, mode: str):
        """Set execution mode"""
        self.mode = DispatchMode(mode)
        logger.info(f"Dispatcher mode changed to: {self.mode.value}")
    
    def dispatch(self, agent, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Dispatch method execution based on current mode
        
        Args:
            agent: Agent instance
            method_name: Method name to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Execution result
        """
        logger.info(f"Dispatching {method_name} in mode {self.mode.value}")
        
        if self.mode == DispatchMode.AUTO:
            return self._auto_mode(agent, method_name, *args, **kwargs)
        elif self.mode == DispatchMode.HUMAN_RELAY:
            return self._human_relay_mode(agent, method_name, *args, **kwargs)
        else:  # MIXED
            return self._mixed_mode(agent, method_name, *args, **kwargs)
    
    def _auto_mode(self, agent, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Fully automated execution"""
        logger.debug(f"Auto mode: executing {method_name}")
        method = getattr(agent, method_name)
        return method(*args, **kwargs)
    
    def _human_relay_mode(self, agent, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Human relay mode"""
        logger.debug(f"Human relay mode: awaiting human decision for {method_name}")
        # TODO: Implement human relay mode UI interaction
        return {"status": "awaiting_human_decision"}
    
    def _mixed_mode(self, agent, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Mixed mode: AI generates draft, human reviews"""
        logger.debug(f"Mixed mode: AI generating draft for {method_name}")
        method = getattr(agent, method_name)
        result = method(*args, **kwargs)
        result["status"] = "draft_generated_awaiting_review"
        return result
