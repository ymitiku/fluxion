import unittest
from unittest.mock import patch, Mock, mock_open
from fluxion.perception.sources.api_sources import APISource
from fluxion.perception.sources.image_sources import (
    RawImageFileSource,
    ScaledImageFileSource,
    ImageEmbeddingSource,
)
from fluxion.perception.sources.text_sources import FileTextSource, StringBufferSource
from PIL import Image
import numpy as np

class TestAPISource(unittest.TestCase):
    @patch("fluxion.core.perception.sources.api_sources.requests.get")
    def test_get_data_success_with_get(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"message": "success"}'
        mock_get.return_value = mock_response

        source = APISource(api_url="https://example.com/api", name="TestAPI")
        data = source.get_data()
        self.assertEqual(data, '{"message": "success"}')

    @patch("fluxion.core.perception.sources.api_sources.requests.post")
    def test_get_data_success_with_post(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"message": "created"}'
        mock_post.return_value = mock_response

        source = APISource(api_url="https://example.com/api", name="TestAPI")
        data = source.get_data(method="POST", data={"key": "value"})
        self.assertEqual(data, '{"message": "created"}')

    def test_get_data_without_api_url(self):
        with self.assertRaises(ValueError):
            source = APISource(name="TestAPI")
            source.get_data()


class TestTextSources(unittest.TestCase):
    def test_file_text_source_success(self):
        mock_file_content = "Hello, world!"
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            source = FileTextSource(file_path="dummy.txt", name="FileSource")
            self.assertEqual(source.get_text(), mock_file_content)

    def test_file_text_source_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            source = FileTextSource(file_path="nonexistent.txt", name="FileSource")
            source.get_text()

    def test_string_buffer_source_with_string(self):
        buffer = "This is a test string."
        source = StringBufferSource(buffer=buffer, name="StringBufferSource")
        self.assertEqual(source.get_text(), buffer)

    def test_string_buffer_source_with_iterable(self):
        buffer = ["This", "is", "a", "test."]
        source = StringBufferSource(buffer=buffer, name="StringBufferSource")
        self.assertEqual(source.get_text(), "This is a test.")

    def test_string_buffer_source_missing_buffer(self):
        source = StringBufferSource(name="StringBufferSource")
        with self.assertRaises(ValueError):
            source.get_text()


class TestImageSources(unittest.TestCase):
    @patch("PIL.Image.open")
    def test_raw_image_file_source(self, mock_open_image):
        mock_image = Mock(spec=Image.Image)
        mock_open_image.return_value = mock_image

        source = RawImageFileSource(image_path="image.png", name="RawImageSource")
        data = source.get_data()
        self.assertIn("image", data)
        self.assertEqual(data["image"], mock_image)

    @patch("PIL.Image.open")
    def test_scaled_image_file_source(self, mock_open_image):
        mock_image = Mock(spec=Image.Image)
        mock_image.resize.return_value = "scaled_image"
        mock_open_image.return_value = mock_image

        source = ScaledImageFileSource(
            image_path="image.png", width=100, height=100, name="ScaledImageSource"
        )
        data = source.get_data()
        self.assertEqual(data["image"], "scaled_image")
        mock_image.resize.assert_called_once_with((100, 100))

    @patch("PIL.Image.open")
    @patch("numpy.expand_dims")
    @patch("fluxion.core.perception.sources.image_sources.np.array")
    def test_image_embedding_source(self, mock_np_array, mock_expand_dims, mock_open_image):
        mock_image = Mock(spec=Image.Image)
        mock_open_image.return_value = mock_image
        mock_np_array.return_value = "numpy_array"
        mock_expand_dims.return_value = "expanded_array"

        mock_model = Mock()
        mock_model.predict.return_value = "embedding"

        source = ImageEmbeddingSource(
            image_path="image.png",
            model=mock_model,
            input_shape=(224, 224),
            name="ImageEmbeddingSource",
        )
        data = source.get_data()
        self.assertEqual(data["image"], "embedding")
        mock_model.predict.assert_called_once_with("expanded_array")


if __name__ == "__main__":
    unittest.main()
