import os

from services.design.figma_services.figma_extraction import run_figma_extraction_pipeline
from services.design.figma_services.extractor.tree_extractor import extract_tree_3levels
from services.design.figma_services.extractor.component_reu import extract_reusable_components
from services.design.figma_services.extractor.prepare_payload import prepare_payload
from services.design.figma_services.planner.analyste import run_analyste
from services.design.figma_services.extractor.image_downloader import download_figma_images_and_rewrite_jsons
from services.design.figma_services.extractor.icon_downloader import run_icon_downloader
from services.design.figma_services.architect.architecte import run_architecte
from services.design.figma_services.extractor.section_extractor import extract_sections
from services.design.figma_services.generator.setup_project import run_setup
from services.design.figma_services.generator.generateur import run_generateur
from services.design.figma_services.generator.generateur import run_generateur_pages_only
from services.design.figma_services.generator.icon_injector import run_icon_injector


from shared.settings import FIGMA_FILE_KEY, RAW_OUTPUT_FILE
from shared.state import GraphState


class FigmaGeneratorAgent:
    def run(self, state: GraphState) -> GraphState:
        try:
            figma_id = state.figma_file_id or FIGMA_FILE_KEY
            # ─── EXTRACTION (sautée si le cache Figma existe déjà) ───
            if not os.path.exists(RAW_OUTPUT_FILE):
                print(f"\n=== FIGMA EXTRACTION (id={figma_id}) ===")
                run_figma_extraction_pipeline(figma_id=figma_id)

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
            else:
                print("[FIGMA] cache présent -> extraction sautée")

            # ─── Génération (tourne toujours) ───
            run_setup()

            #run_generateur_pages_only()
            run_generateur()

            

            state.workflow_state = "figma_generation_done"

        except Exception as e:
            state.workflow_state = "figma_generation_failed"
            state.error_log = (state.error_log or "") + f"\n[FIGMA GENERATOR ERROR] {str(e)}"

        return state