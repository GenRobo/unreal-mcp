"""
Gaussian Splat / SOG Tools for Unreal MCP.

This module provides tools for querying and debugging Gaussian Splat assets and components
in Unreal Engine, including SOG (Spatially Ordered Gaussians) runtime data.
"""

import logging
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context

# Get logger
logger = logging.getLogger("UnrealMCP")


def register_gaussian_splat_tools(mcp: FastMCP):
    """Register Gaussian Splat / SOG query tools with the MCP server."""

    @mcp.tool()
    def get_splat_components(ctx: Context) -> Dict[str, Any]:
        """
        Get all Gaussian Splat components in the current level.
        
        Returns:
            Dict with 'components' array and 'count' field
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"error": "Not connected to Unreal Engine", "components": [], "count": 0}
            
            response = unreal.send_command("get_splat_components", {})
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"error": "No response", "components": [], "count": 0}
            
            result = response.get("result", response)
            logger.info(f"Found {result.get('count', 0)} splat components")
            return result
            
        except Exception as e:
            logger.error(f"Error getting splat components: {e}")
            return {"error": str(e), "components": [], "count": 0}

    @mcp.tool()
    def get_splat_component_info(ctx: Context, actor_name: str) -> Dict[str, Any]:
        """
        Get detailed info about a specific Gaussian Splat component.
        
        Args:
            actor_name: Name or partial name of the actor containing the splat component
            
        Returns:
            Dict with component properties including asset info, transform, and render settings
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"error": "Not connected to Unreal Engine"}
            
            response = unreal.send_command("get_splat_component_info", {
                "actor_name": actor_name
            })
            
            if not response:
                return {"error": "No response"}
            
            return response.get("result", response)
            
        except Exception as e:
            logger.error(f"Error getting splat component info: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_splat_asset_info(ctx: Context, asset_name: str) -> Dict[str, Any]:
        """
        Get detailed info about a Gaussian Splat asset.
        
        Args:
            asset_name: Name or partial name of the splat asset
            
        Returns:
            Dict with asset properties including num_points, bounds, textures, and SOG metadata
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"error": "Not connected to Unreal Engine"}
            
            response = unreal.send_command("get_splat_asset_info", {
                "asset_name": asset_name
            })
            
            if not response:
                return {"error": "No response"}
            
            return response.get("result", response)
            
        except Exception as e:
            logger.error(f"Error getting splat asset info: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def list_splat_assets(ctx: Context) -> Dict[str, Any]:
        """
        List all Gaussian Splat assets in the project.
        
        Returns:
            Dict with 'assets' array containing name, path, num_points, is_sog for each asset
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"error": "Not connected to Unreal Engine", "assets": [], "count": 0}
            
            response = unreal.send_command("list_splat_assets", {})
            
            if not response:
                return {"error": "No response", "assets": [], "count": 0}
            
            result = response.get("result", response)
            logger.info(f"Found {result.get('count', 0)} splat assets")
            return result
            
        except Exception as e:
            logger.error(f"Error listing splat assets: {e}")
            return {"error": str(e), "assets": [], "count": 0}

    @mcp.tool()
    def get_sog_metadata(ctx: Context, asset_name: str) -> Dict[str, Any]:
        """
        Get SOG-specific decode metadata for an asset.
        
        Args:
            asset_name: Name of the SOG asset
            
        Returns:
            Dict with SOG decode parameters:
            - means.mins/maxs: Log-domain ranges for position decode
            - bounds: World-space bounds (origin, extent, sphere_radius)
            - textures: Info about each SOG texture (means_lower, means_upper, quats, scales, sh0, etc.)
            - codebook sizes for scales, sh0, shn
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"error": "Not connected to Unreal Engine"}
            
            response = unreal.send_command("get_sog_metadata", {
                "asset_name": asset_name
            })
            
            if not response:
                return {"error": "No response"}
            
            return response.get("result", response)
            
        except Exception as e:
            logger.error(f"Error getting SOG metadata: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_sog_codebook(
        ctx: Context, 
        asset_name: str, 
        codebook_type: str = "scales"
    ) -> Dict[str, Any]:
        """
        Get the codebook values for a SOG asset.
        
        Args:
            asset_name: Name of the SOG asset
            codebook_type: Type of codebook - 'scales', 'sh0', or 'shn'
            
        Returns:
            Dict with:
            - values: Array of 256 float values
            - min/max/mean: Statistics
            - size: Number of entries
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"error": "Not connected to Unreal Engine"}
            
            response = unreal.send_command("get_sog_codebook", {
                "asset_name": asset_name,
                "codebook_type": codebook_type
            })
            
            if not response:
                return {"error": "No response"}
            
            return response.get("result", response)
            
        except Exception as e:
            logger.error(f"Error getting SOG codebook: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def decode_splat_positions(
        ctx: Context,
        asset_name: str,
        indices: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Get decode parameters for specific splat positions.
        
        Note: Full CPU texture decode is expensive. This returns decode parameters
        so external tools can understand the pipeline.
        
        Args:
            asset_name: Name of the SOG asset
            indices: Optional list of splat indices to decode (default: first 10)
            
        Returns:
            Dict with decode_params (mins, maxs) and bounds_center
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"error": "Not connected to Unreal Engine"}
            
            params = {"asset_name": asset_name}
            if indices:
                params["indices"] = indices
            
            response = unreal.send_command("decode_splat_positions", params)
            
            if not response:
                return {"error": "No response"}
            
            return response.get("result", response)
            
        except Exception as e:
            logger.error(f"Error decoding splat positions: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def sample_splat_positions(
        ctx: Context,
        asset_name: str,
        count: int = 10
    ) -> Dict[str, Any]:
        """
        Get sampled splat positions from an asset.
        
        For legacy assets, returns actual positions.
        For SOG assets, returns texture coordinates (actual decode requires GPU).
        
        Args:
            asset_name: Name of the splat asset
            count: Number of samples to return (1-100)
            
        Returns:
            Dict with 'samples' array containing positions or texture coords
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"error": "Not connected to Unreal Engine"}
            
            response = unreal.send_command("sample_splat_positions", {
                "asset_name": asset_name,
                "count": min(max(count, 1), 100)
            })
            
            if not response:
                return {"error": "No response"}
            
            return response.get("result", response)
            
        except Exception as e:
            logger.error(f"Error sampling splat positions: {e}")
            return {"error": str(e)}

    @mcp.tool()
    def get_splat_render_stats(ctx: Context) -> Dict[str, Any]:
        """
        Get render statistics for all Gaussian Splat components.
        
        Returns:
            Dict with:
            - total_components: Number of splat components in the level
            - total_splat_points: Sum of all splat points
            - sog_components: Number using SOG format
            - legacy_components: Number using legacy format
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"error": "Not connected to Unreal Engine"}
            
            response = unreal.send_command("get_splat_render_stats", {})
            
            if not response:
                return {"error": "No response"}
            
            result = response.get("result", response)
            logger.info(f"Render stats: {result.get('total_components', 0)} components, "
                       f"{result.get('total_splat_points', 0)} total points")
            return result
            
        except Exception as e:
            logger.error(f"Error getting render stats: {e}")
            return {"error": str(e)}
