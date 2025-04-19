import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Textarea,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  VStack,
  Text,
  useToast,
  Spinner,
} from '@chakra-ui/react';

interface ProcessedText {
  summary: string;
  translation: string;
}

const TextProcessor: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [maxLength, setMaxLength] = useState(150);
  const [targetLang, setTargetLang] = useState('Hindi');
  const [processedText, setProcessedText] = useState<ProcessedText | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputText.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter some text to process',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsLoading(true);
    setProcessedText(null);

    try {
      const response = await fetch('http://localhost:8000/text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          max_length: maxLength,
          target_lang: targetLang,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process text');
      }

      const data = await response.json();
      setProcessedText(data);
      toast({
        title: 'Success',
        description: 'Text processed successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error:', error);
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to process text',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const languages = [
    'Hindi',
    'Spanish',
    'French',
    'German',
    'Italian',
    'Portuguese',
    'Russian',
    'Japanese',
    'Korean',
    'Chinese',
  ];

  return (
    <Box maxW="800px" mx="auto" p={4}>
      <form onSubmit={handleSubmit}>
        <VStack spacing={4} align="stretch">
          <FormControl isRequired>
            <FormLabel>Enter your text</FormLabel>
            <Textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter text to process..."
              size="lg"
              minH="200px"
              isDisabled={isLoading}
            />
          </FormControl>

          <FormControl>
            <FormLabel>Maximum summary length (characters)</FormLabel>
            <NumberInput
              value={maxLength}
              onChange={(_, value) => setMaxLength(value)}
              min={50}
              max={500}
              isDisabled={isLoading}
            >
              <NumberInputField />
              <NumberInputStepper>
                <NumberIncrementStepper />
                <NumberDecrementStepper />
              </NumberInputStepper>
            </NumberInput>
          </FormControl>

          <FormControl>
            <FormLabel>Target Language</FormLabel>
            <Select
              value={targetLang}
              onChange={(e) => setTargetLang(e.target.value)}
              isDisabled={isLoading}
            >
              {languages.map((lang) => (
                <option key={lang} value={lang}>
                  {lang}
                </option>
              ))}
            </Select>
          </FormControl>

          <Button
            type="submit"
            colorScheme="blue"
            isLoading={isLoading}
            loadingText="Processing..."
          >
            Process Text
          </Button>

          {isLoading && (
            <Box textAlign="center" py={4}>
              <Spinner size="xl" />
              <Text mt={2}>Processing your text...</Text>
            </Box>
          )}

          {processedText && (
            <VStack spacing={4} align="stretch" mt={4}>
              <Box borderWidth={1} borderRadius="md" p={4}>
                <Text fontWeight="bold" mb={2}>
                  Summary:
                </Text>
                <Text>{processedText.summary}</Text>
              </Box>

              <Box borderWidth={1} borderRadius="md" p={4}>
                <Text fontWeight="bold" mb={2}>
                  Translation ({targetLang}):
                </Text>
                <Text>{processedText.translation}</Text>
              </Box>
            </VStack>
          )}
        </VStack>
      </form>
    </Box>
  );
};

export default TextProcessor; 