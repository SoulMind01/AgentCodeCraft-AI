import React from 'react';
import { Center, Text } from '@chakra-ui/react';

interface ErrorStateProps {
  message?: string;
}

const ErrorState: React.FC<ErrorStateProps> = ({
  message = 'Something went wrong.',
}) => (
  <Center py={8}>
    <Text fontSize="sm" color="red.600">
      {message}
    </Text>
  </Center>
);

export default ErrorState;