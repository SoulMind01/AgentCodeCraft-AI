import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Center, Heading, Text, Link, VStack } from '@chakra-ui/react';

const NotFoundPage: React.FC = () => (
  <Center py={24}>
    <VStack spacing={2}>
      <Heading as="h1" size="lg">
        404 - Not Found
      </Heading>
      <Text fontSize="sm" color="gray.600">
        The page you are looking for does not exist.
      </Text>
      <Box mt={2}>
        <Link as={RouterLink} to="/runs" fontSize="sm" color="blue.600">
          Go to dashboard
        </Link>
      </Box>
    </VStack>
  </Center>
);

export default NotFoundPage;