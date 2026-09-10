from mcp.server.fastmcp import FastMCP
from .core.service import Service
s=Service();mcp=FastMCP('hybrid-eps',instructions='Inspect and analyze before export. Every write requires exact plan approval and asynchronous verified execution. Paths are confined to HYBRID_EPS_ROOT.')
@mcp.tool()
def eps_get_capabilities()->dict:"""Discover formats, algorithms, versions and limits.""";return s.capabilities()
@mcp.tool()
def eps_inspect_image(path:str)->dict:"""Validate and inspect raster content, dimensions, frames, metadata and hash.""";return s.inspect(path)
@mcp.tool()
def eps_analyze_edges(path:str,edge_settings:dict,vector_settings:dict)->dict:"""Run edge/vector analysis without writing files.""";return s.analyze(path,edge_settings,vector_settings)
@mcp.tool()
def eps_compare_methods(path:str,methods:list[str],base_edge_settings:dict)->dict:"""Compare Canny/Sobel/Laplacian/Scharr metrics for informed selection.""";return s.compare(path,methods,base_edge_settings)
@mcp.tool()
def eps_list_presets()->dict:return s.presets
@mcp.tool()
def eps_validate_settings(edge_settings:dict,vector_settings:dict,export_settings:dict)->dict:
 from .models import EdgeSettings,VectorSettings,ExportSettings
 return {'edge':EdgeSettings(**edge_settings).model_dump(),'vector':VectorSettings(**vector_settings).model_dump(),'export':ExportSettings(**export_settings).model_dump()}
@mcp.tool()
def eps_plan_export(input_path:str,output_path:str,edge_settings:dict,vector_settings:dict,export_settings:dict)->dict:"""Plan one exact hybrid/vector export; does not write.""";return s.plan_export(input_path,output_path,edge_settings,vector_settings,export_settings)
@mcp.tool()
def eps_plan_batch(inputs:list[str],output_directory:str,edge_settings:dict,vector_settings:dict,export_settings:dict,suffix:str='_hybrid')->dict:"""Plan up to 1000 exports with collision disclosure.""";return s.plan_batch(inputs,output_directory,edge_settings,vector_settings,export_settings,suffix)
@mcp.tool()
def eps_approve(plan_id:str,explicit_approval:str)->dict:"""Issue exact 60-second single-use approval.""";return s.approval.approve(plan_id,explicit_approval)
@mcp.tool()
def eps_execute(plan_id:str,approval_token:str)->dict:"""Start approved export as bounded worker job.""";return s.execute(plan_id,approval_token)
@mcp.tool()
def eps_get_job(job_id:str)->dict:return s.status(job_id)
@mcp.tool()
def eps_cancel_job(job_id:str,confirmation:str)->dict:
 if confirmation!='CANCEL':raise ValueError('confirmation must equal CANCEL')
 return s.cancel_job(job_id)
@mcp.tool()
def eps_get_algorithm_guidance()->dict:return {'canny':'clean linked binary edges; thresholds matter','sobel':'first derivative magnitude; directional gradients','scharr':'more accurate 3x3 derivative than Sobel','laplacian':'second derivative; noise sensitive','vectorization':'binary edge map → findContours hierarchy → Douglas-Peucker simplification','format_notes':{'svg':'explicit paths and optional embedded PNG; best inspectability','eps':'PostScript vector paths plus optional raster; transparency limited','pdf':'portable hybrid vector/raster','png':'rasterized final composition'}}
def main():mcp.run(transport='stdio')
if __name__=='__main__':main()
