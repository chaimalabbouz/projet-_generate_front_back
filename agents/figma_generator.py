from figma_services.figma_extraction import run_figma_extraction_pipeline
from figma_services.extractor.tree_extractor import extract_tree_3levels
from figma_services.extractor.component_reu import extract_reusable_components
from figma_services.extractor.prepare_payload import prepare_payload
from figma_services.planner.analyste import run_analyste
from figma_services.extractor.image_downloader import download_figma_images_and_rewrite_jsons
from figma_services.extractor.icon_downloader import run_icon_downloader
from figma_services.architect.architecte import run_architecte
from figma_services.extractor.section_extractor import extract_sections
from figma_services.generator.setup_project import run_setup
from figma_services.generator.generateur import run_generateur
from figma_services.generator.generateur import run_generateur_pages_only
from figma_services.generator.icon_injector import run_icon_injector
from figma_services.generator.val import run_validateur

from config.settings import FIGMA_FILE_KEY
from orchestrator.state import GraphState


class FigmaGeneratorAgent:
    def run(self, state: GraphState) -> GraphState:
        try:
            # ─── Récupération du Figma (avec ID dynamique) ───
            print("\n=== ETAPE 0: FIGMA EXTRACTION ===")
            run_figma_extraction_pipeline(figma_id=FIGMA_FILE_KEY)

            # ─── Extraction ───
            
            extract_tree_3levels()

            
            extract_reusable_components()

            
            prepare_payload()

            # ─── Planning ───
            
            run_analyste()

            
            run_architecte()

           
            extract_sections()
            download_figma_images_and_rewrite_jsons()

            
            #run_icon_downloader()

            # ─── Génération ───
            
            run_setup()

            
            #run_generateur_pages_only()
            run_generateur()
            
            run_icon_injector()

            
            #run_validateur()

            

            state.workflow_state = "figma_generation_done"

        except Exception as e:
            state.workflow_state = "figma_generation_failed"
            state.error_log = (state.error_log or "") + f"\n[FIGMA GENERATOR ERROR] {str(e)}"

        return state