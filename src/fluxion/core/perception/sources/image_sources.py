from abc import abstractmethod, ABC
from typing import Dict, Any, Union,  Tuple
from fluxion.core.perception.sources.perception_source import PerceptionSource
from PIL import Image
import numpy as np

class ImageSource(PerceptionSource, ABC):
    def __init__(self, image_path: str = None, **kwargs: Dict[str, Any]):
        """
        Initialize the ImageSource with the image path.

        Args:
            image_path (str): The path to the image file
        """
        if "name" not in kwargs:
            kwargs["name"] = "ImageSource"
        super().__init__(**kwargs)
        self.image_path = image_path

    def get_data(self, **kwargs) -> str:
        image = self.load_image(self.image_path)
        processed_image = self.process_image(image)
        return {"image": processed_image}

    @abstractmethod
    def load_image(self, image_path: str) -> Union[np.ndarray, Image.Image]:
        """
        Load the image from the given path.

        Args:
            image_path (str): The path to the image file

        Returns:
            np.ndarray: The image as a numpy array or PIL Image
        """
        pass

    @abstractmethod
    def process_image(self, image: Union[np.ndarray, Image.Image]) -> Union[np.ndarray, Image.Image]:
        """
        Process the image.

        Args:
            image (np.ndarray): The image as a numpy array or PIL Image

        Returns:
            np.ndarray: The processed image as a numpy array or PIL Image
        """
        pass

class RawImageFileSource(ImageSource):
    def load_image(self, image_path: str) -> Image.Image:
        return Image.open(image_path)
        

    def process_image(self, image: np.ndarray) -> np.ndarray:
        return image


class ScaledImageFileSource(RawImageFileSource):
    def __init__(self, width: int, height: int, **kwargs: Dict[str, Any]):
        """
        Initialize the ScaledImageFileSource with the scale factor.

        Args:
            width (int): The width of the scaled image
            height (int): The height of the scaled image
        """
        super().__init__(**kwargs)
        self.width = width
        self.height = height

    def process_image(self, image: Image) -> Image:
        return image.resize((self.width, self.height))
    

class ImageEmbeddingSource(ScaledImageFileSource):
    def __init__(self, model: Any, input_shape:  Tuple[int, int],  **kwargs: Dict[str, Any]):
        """
        Initialize the ImageEmbeddingSource with the embedding model.

        Args:
            model (Any): The image embedding model
            input_shape (Tuple[int, int]): The input shape of the model(widht, height)

        """
        super().__init__(*input_shape, **kwargs)
        self.model = model


    def process_image(self, image: np.ndarray) -> np.ndarray:
        image = super().process_image(image)
        image = np.array(image)
        image = np.expand_dims(image, axis=0)
        return self.model.predict(image)
    
    