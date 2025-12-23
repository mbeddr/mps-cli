from mpscli.model.builder.SModelBuilderBase import SModelBuilderBase
import uuid


class SModelBuilderBinaryPersistency(SModelBuilderBase):

    # the following constants are taked from the MPS sources found at:
    #   https://github.com/JetBrains/MPS/blob/f9075b2832077358fd85a15a52bba76a9dad07a3/core/persistence/source/jetbrains/mps/persistence/binary/BinaryPersistence.java#L82
    HEADER_START = 0x91ABABA9
    STREAM_ID_V2 = 0x00000400

    # https://github.com/JetBrains/MPS/blob/f9075b2832077358fd85a15a52bba76a9dad07a3/core/kernel/source/jetbrains/mps/util/io/ModelOutputStream.java
    MODELREF_INDEX = 9
    MODELID_REGULAR = 0x28

    def build(self, path_to_model):
        print("Building binary persistency model from:", path_to_model)
        with open(path_to_model, mode='rb') as file: 
            fileContent = file.read()
            header = int.from_bytes(fileContent[:4], byteorder='big')
            if header != self.HEADER_START:
                raise ValueError("Invalid file format")
            streamId = int.from_bytes(fileContent[4:8], byteorder='big')
            if streamId != self.STREAM_ID_V2:
                raise ValueError("Unsupported stream ID")
            modelRef = self.readModelReference(fileContent, 8)
        # Implement the binary persistency model building logic here
        pass



    def readModelReference(self, fileContent, pos):
        modelRefIndex = int.from_bytes(fileContent[pos:pos+2], byteorder='big')
        if modelRefIndex != self.MODELREF_INDEX:
            return self.readModelId(fileContent, pos+2)
        pass

    def readModelId(self, fileContent, pos):
        print("Reading Model ID at position:", pos)
        modelId = int.from_bytes(fileContent[pos:pos+1], byteorder='big')
        if modelId == self.MODELID_REGULAR:
            return self.readUUID(fileContent, pos+1)
        else:
            print(f"Error: unhandled model ID type: 0x{modelId:X}")
        return None
    

    def readUUID(self, fileContent, pos):
        headBits = self.readLong(fileContent, pos)
        tailBits = self.readLong(fileContent, pos + 8)
        uuid_val = uuid.UUID(int=(headBits << 64) | tailBits)
        print("------------ UUID:", uuid_val)
        return (headBits, tailBits)

    def readLong(self, fileContent, pos):
        return int.from_bytes(fileContent[pos:pos+8], byteorder='big')