from app.rag.vector_store import vector_store


class DocumentManager:

    def list_documents(self):

        documents = vector_store.get_documents()

        return [
            {
                "filename": filename,
                "chunks": count
            }
            for filename, count in documents.items()
        ]


    def delete_document(
        self,
        filename: str
    ):

        if not vector_store.document_exists(filename):

            return {
                "status": "not_found",
                "filename": filename
            }

        vector_store.delete_document(filename)

        return {
            "status": "deleted",
            "filename": filename
        }


document_manager = DocumentManager()