import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import type { RunSummary } from '../../api/types';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Tag,
  Link,
  Text,
} from '@chakra-ui/react';

interface Props {
  runs: RunSummary[];
}

const statusColor: Record<string, string> = {
  queued: 'gray',
  running: 'blue',
  done: 'green',
  failed: 'red',
};

const RunTable: React.FC<Props> = ({ runs }) => {
  if (!runs.length) {
    return (
      <Text fontSize="sm" color="gray.500">
        No runs yet.
      </Text>
    );
  }

  return (
    <Box borderWidth="1px" borderRadius="md" bg="white" overflowX="auto">
      <Table size="sm">
        <Thead bg="gray.50">
          <Tr>
            <Th>Run ID</Th>
            <Th>Status</Th>
            <Th>Language</Th>
            <Th>Score</Th>
            <Th>Started</Th>
            <Th>Action</Th>
          </Tr>
        </Thead>
        <Tbody>
          {runs.map((run) => (
            <Tr key={run.run_id}>
              <Td>
                <Text fontFamily="mono" fontSize="xs">
                  {run.run_id}
                </Text>
              </Td>
              <Td>
                <Tag
                  size="sm"
                  colorScheme={statusColor[run.status] || 'gray'}
                  borderRadius="full"
                >
                  {run.status}
                </Tag>
              </Td>
              <Td>{run.language}</Td>
              <Td>
                {run.compliance_score != null
                  ? `${Math.round(run.compliance_score * 100)}%`
                  : '—'}
              </Td>
              <Td fontSize="xs" color="gray.500">
                {new Date(run.started_at).toLocaleString()}
              </Td>
              <Td>
                <Link
                  as={RouterLink}
                  to={`/runs/${run.run_id}`}
                  fontSize="xs"
                  color="blue.600"
                >
                  View
                </Link>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

export default RunTable;