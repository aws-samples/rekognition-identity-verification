from typing import List, Mapping
from json import dumps

#from aws_xray_sdk.core import xray_recorder
from model import BlockType, DocumentKeyValueBlock, IDocumentBlock, ITextractDocument

class DocumentParser:
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
