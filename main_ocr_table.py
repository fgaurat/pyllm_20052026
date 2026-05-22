from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice, TableFormerMode
)
from docling.datamodel.base_models import InputFormat


def main():

    opts = PdfPipelineOptions()
    opts.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CPU)

    # Mode précis pour la structure des tableaux
    opts.do_table_structure = True
    opts.table_structure_options.mode = TableFormerMode.ACCURATE
    # Aligne les cellules sur le texte natif du PDF (clé pour récupérer le "44 000")
    opts.table_structure_options.do_cell_matching = True

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )

    result = converter.convert("./corpus_tp/cptres1.pdf")

    with open("cptres1_2.md", "w") as f:
        f.write(result.document.export_to_markdown())

if __name__=='__main__':
    main()
