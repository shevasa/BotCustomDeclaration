def create_state_dict(all_needed_documents: list):
    dictionary = dict()
    for document_dict in all_needed_documents:
        document_type_name = document_dict.get('document_type_name')
        dictionary[f'{document_type_name}'] = list()
    return dictionary
