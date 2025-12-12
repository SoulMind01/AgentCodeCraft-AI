import React from 'react';
import { Center, Spinner, Text, VStack } from '@chakra-ui/react';

interface LoaderProps {
  message?: string;
}

const Loader: React.FC<LoaderProps> = ({ message = 'Loading...' }) => (
  <Center py={8}>
    <VStack spacing={3}>
      <Spinner />
      <Text fontSize="sm" color="gray.600">
        {message}
      </Text>
    </VStack>
  </Center>
);

export default Loader;