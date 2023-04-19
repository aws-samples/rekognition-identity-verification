from typing import List, Mapping
from json import dumps

#from aws_xray_sdk.core import xray_recorder
from model import BlockType, DocumentKeyValueBlock, IDocumentBlock, ITextractDocument

class DocumentParser:
  '''
  Represents a utility for parsing the response from Textract:AnalzyeDocument.
    
    Note: This was the preferred way to import an ID Card during RIV v1.
    Since then, Textract:AnalyzeId became available and is purpose-built for our use-case.

  :example:
  response = textract_client.analyze_document(...)
  parser = DocumentParser(TextractDocument(response))` for more fine-grained control.    
  properties = inputRequest.property_bag
  form = parser.extract_form()
  for key in form.keys():
    properties[key] = form[key]
  '''
  def __init__(self, document:ITextractDocument) -> None:
    self.document = document

  def pretty_print(self, block_type=BlockType.PAGE)->str:
    '''
    Create a developer friendly representation.
    '''
    root_blocks = self.document.find_blocks(block_type)
    
    tree = []
    for block in root_blocks:
      tree.append(block.to_dict())

    return dumps(tree,indent=2)

  #@xray_recorder.capture('DocumentParser::extract_form')
  def extract_form(self)->Mapping[str,str]:
    '''
    Extracts a mapping of idcard properties to values.
    '''
    keyValueBlocks:List[DocumentKeyValueBlock] = self.document.find_blocks(BlockType.KEY_VALUE_SET)
    form:Mapping[str, List[IDocumentBlock]] = {}
    for kvb in keyValueBlocks:
      if not 'KEY' in kvb.entity_types:
        continue

      form[kvb.get_key_text()] = kvb.get_value_text()
    return form      
