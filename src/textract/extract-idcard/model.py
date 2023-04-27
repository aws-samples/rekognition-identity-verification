from enum import Enum
from typing import List, Mapping
from base64 import b64decode
#from aws_xray_sdk.core import xray_recorder

class InvalidImageError(Exception):
  '''
  Represents an error due to invalid image.
  '''
  pass

class TransientError(Exception):
  '''
  Represents a transient and retryable failure. 
  '''
  pass

class InputRequest:
  '''
  Represents the Lambda function input request.
  '''
  def __init__(self, event:Mapping[str,str]) -> None:
    assert event is not None, "No event specified."
    assert 'UserId' in event, "Missing required event.UserId attribute"
    assert 'IdCard' in event, "Missing required event.IdCard attribute"
    assert 'ImageName' in event, "Missing required event.ImageName attribute"
      

    self.__user_id = event['UserId']
    self.__idcard_image = b64decode(event['IdCard'])
    self.__image_name = event['ImageName']
    
    if 'Properties' in event:
      self.__properties = event['Properties']
    else:
      self.__properties = {}

  @property
  def user_id(self)->str:
    return self.__user_id

  @property
  def idcard_image_bytes(self)->bytes:
    return self.__idcard_image

  @property
  def idcard_image_bytes(self) -> bytes:
        return self.__idcard_image

  @property
  def property_bag(self)->dict:
    return self.__properties

class BlockType(Enum):
    '''
    Represents the known Document Block types.
    '''
    PAGE = 'PAGE'
    LINE = 'LINE'
    KEY_VALUE_SET = 'KEY_VALUE_SET'
    WORD = 'WORD'


class IDocumentBlock:
    '''
    Represents an interface into a DocumentBlock.
    '''

    def __init__(self, props: dict) -> None:
        self.block_type: BlockType = BlockType(props['BlockType'])
        self.geometry = BlockGeometry(props['Geometry'])
        self.id: str = props['Id']

    def to_dict(self) -> dict:
        raise NotImplementedError(self.__class__.__name__)


class ITextractDocument:
    '''
    Represents an interface for interacting with a Textract Response.
    '''
    @property
    def blocks(self) -> List[IDocumentBlock]:
        '''
        Gets a list of all Document Blocks.
        '''
        return self.__blocks

    @blocks.setter
    def blocks(self, value: List[IDocumentBlock]) -> None:
        '''
        Sets the list of all Document Blocks.
        '''
        self.__blocks = value

    def find_blocks(self, id: str) -> IDocumentBlock:
        assert id is not None, "missing id argument"
        raise NotImplementedError()

    def find_blocks(self, block_type: BlockType) -> List[IDocumentBlock]:
        assert block_type is not None, "Missing block_type"
        return [x for x in self.blocks if x.block_type == block_type]


class BlockBoundingBox:
    '''
    Represents the a box around the textual element.
      All properties are scaled between 0 to 1.
      To normalize multiple the dimensions by the image size.
    '''

    def __init__(self, props: dict) -> None:
        self.width: float = props['Width']
        self.height: float = props['Height']
        self.left: float = props['Left']
        self.top: float = props['Top']


class BlockPolygonPoint:
    def __init__(self, props: dict) -> None:
        self.x: float = props['X']
        self.y: float = props['Y']


class BlockPolygon:
    def __init__(self, props: dict) -> None:
        self.points = [BlockPolygonPoint(x) for x in props]


class BlockGeometry:
    def __init__(self, props: dict) -> None:
        self.bounding_box: dict = BlockBoundingBox(props['BoundingBox'])
        self.polygon: List[dict] = props['Polygon']


class RelationshipCollection:
    def __init__(self, owning_document: ITextractDocument, props: dict) -> None:
        self.owning_document: ITextractDocument = owning_document
        self.type = props['Type']
        self.ids: List[str] = props['Ids']
        self.__blocks = None

    @property
    def blocks(self) -> IDocumentBlock:
        if self.__blocks is None:
            self.__blocks: List[IDocumentBlock] = [
                self.owning_document.find_block(x) for x in self.ids
            ]
        return self.__blocks

    def get_text(self) -> str:
        words: List[str] = []
        for block in self.blocks:
            if block.block_type == BlockType.WORD:
                block: DocumentWordBlock = block
                words.append(block.text)
            elif block.block_type == BlockType.LINE:
                block: DocumentLineBlock = block
                words.append(block.text)
            elif block.block_type == BlockType.KEY_VALUE_SET:
                block: DocumentKeyValueBlock = block
                words.append(block.get_text())
            else:
                raise NotImplementedError(block.block_type.name)

        return ' '.join(words)

    def to_dict(self) -> dict:
        return {
            'Class': RelationshipCollection.__name__,
            'Type': self.type,
            'Blocks': [x.to_dict() for x in self.blocks]
        }


class DocumentHierarchicalBlock(IDocumentBlock):
    '''
    Represents a document block element that contains relationships.
    '''

    def __init__(self, owning_document: ITextractDocument, props: dict) -> None:
        super().__init__(props)

        self.owning_document = owning_document

        if 'Relationships' in props:
            self.relationships: Mapping[str, RelationshipCollection] = {}
            for relation in props['Relationships']:
                relation = RelationshipCollection(owning_document, relation)
                self.relationships[relation.type] = relation
        else:
            self.relationships: Mapping[str, RelationshipCollection] = {}


class DocumentPageBlock(DocumentHierarchicalBlock):
    def __init__(self, owning_document: ITextractDocument, props: dict) -> None:
        super().__init__(owning_document, props)

    def to_dict(self) -> dict:
        return {
            'Type': self.block_type.PAGE.name,
            'Children': [x.to_dict() for x in self.relationships.values()]
        }


class DocumentLineBlock(DocumentHierarchicalBlock):
    def __init__(self, owning_document: ITextractDocument, props: dict) -> None:
        super().__init__(owning_document, props)

        self.confidence: float = props['Confidence']
        self.text: str = props['Text']

    def to_dict(self) -> dict:
        return {
            'Class': DocumentLineBlock.__name__,
            'Text': self.text,
            'Children': [x.to_dict() for x in self.relationships.values()]
        }


class DocumentWordBlock(IDocumentBlock):
    def __init__(self, props: dict) -> None:
        super().__init__(props)
        self.confidence: float = props['Confidence']
        self.text: str = props['Text']
        self.text_type: str = props['TextType']

    def to_dict(self) -> dict:
        return {
            'Class': self.__class__.__name__,
            'Text': self.text,
            'TextType': self.text_type
        }


class DocumentKeyValueBlock(DocumentHierarchicalBlock):
    def __init__(self, owning_document: ITextractDocument, props: dict) -> None:
        super().__init__(owning_document, props)

        self.confidence: float = props['Confidence']
        self.entity_types: List[str] = props['EntityTypes']

    def get_key_text(self) -> str:
        return self.relationships['CHILD'].get_text()

    def get_value_text(self) -> str:
        return self.relationships['VALUE'].get_text()

    def get_text(self) -> str:
        if 'VALUE' in self.entity_types:
            return self.relationships['CHILD'].get_text()

        # TODO: Are there more cases to support?
        raise NotImplementedError()

    def to_dict(self) -> dict:
        return {
            'Class': self.__class__.__name__,
            'EntityTypes': self.entity_types,
            'Children': [x.to_dict() for x in self.relationships.values()]
        }


class DocumentBlock:

    @staticmethod
    def create(owning_document: ITextractDocument, props: dict) -> IDocumentBlock:
        block_type: BlockType = BlockType(props['BlockType'])

        if block_type == BlockType.PAGE:
            return DocumentPageBlock(owning_document, props)
        if block_type == BlockType.LINE:
            return DocumentLineBlock(owning_document, props)
        if block_type == BlockType.WORD:
            return DocumentWordBlock(props)
        if block_type == BlockType.KEY_VALUE_SET:
            return DocumentKeyValueBlock(owning_document, props)


class TextractDocument(ITextractDocument):
    '''
    Represents an Amazon Textract response document.
    '''
    # @xray_recorder.capture('TextractDocument::__init__')

    def __init__(self, document: dict) -> None:
        assert document is not None, "No document provided"
        assert 'DocumentMetadata' in document, "document missing DocumentMetadata attribute"
        assert 'Blocks' in document, "document missing Blocks attribute"

        self.document_metadata = document['DocumentMetadata']
        self.blocks = [DocumentBlock.create(
            self, x) for x in document['Blocks']]

        '''
    Build an index for finding blocks by id.
    '''
        self.__block_index: Mapping[str, DocumentBlock] = {}
        for block in self.blocks:
            self.__block_index[block.id] = block

    def find_block(self, id: str) -> IDocumentBlock:
        '''
        Gets a block from the Amazon Textract document.
        '''
        if not id in self.__block_index:
            raise ValueError('Unable to find_block(%s)' % id)
        return self.__block_index[id]