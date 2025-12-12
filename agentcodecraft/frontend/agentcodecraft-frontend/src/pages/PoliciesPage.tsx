import React from 'react';
import {
  Box,
  Heading,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
} from '@chakra-ui/react';
import { usePolicies } from '../api/hooks';
import Loader from '../components/shared/Loader';
import ErrorState from '../components/shared/ErrorState';

const PoliciesPage: React.FC = () => {
  const { data: policies, isLoading, isError } = usePolicies();

  return (
    <Box maxW="800px">
      <Heading as="h1" size="md" mb={4}>
        Policies
      </Heading>

      {isLoading && <Loader message="Loading policies..." />}
      {isError && <ErrorState message="Failed to load policies." />}
      {policies && (
        <Box borderWidth="1px" borderRadius="md" bg="white" overflowX="auto">
          <Table size="sm">
            <Thead bg="gray.50">
              <Tr>
                <Th>Name</Th>
                <Th>Language</Th>
                <Th>Version</Th>
                <Th>Created</Th>
              </Tr>
            </Thead>
            <Tbody>
              {policies.map((p) => (
                <Tr key={p.policy_id}>
                  <Td>{p.name}</Td>
                  <Td>{p.language}</Td>
                  <Td>{p.version}</Td>
                  <Td fontSize="xs" color="gray.500">
                    {new Date(p.created_at).toLocaleString()}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}

      <Text fontSize="xs" color="gray.500" mt={2}>
        TODO: Add YAML editor and /api/policies/validate integration.
      </Text>
    </Box>
  );
};

export default PoliciesPage;