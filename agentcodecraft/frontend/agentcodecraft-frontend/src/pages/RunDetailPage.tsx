import React from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Flex,
  Heading,
  Text,
  SimpleGrid,
  Link,
  VStack,
} from '@chakra-ui/react';
import { useRun } from '../api/hooks';
import Loader from '../components/shared/Loader';
import ErrorState from '../components/shared/ErrorState';

const RunDetailPage: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const { data: run, isLoading, isError } = useRun(runId || '');

  if (!runId) return <ErrorState message="Missing run ID." />;

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={4}>
        <Box>
          <Heading as="h1" size="md">
            Run {runId}
          </Heading>
          {run && (
            <Text fontSize="xs" color="gray.500">
              Model {run.model_version} • Language {run.language}
            </Text>
          )}
        </Box>
        <Link as={RouterLink} to="/runs" fontSize="sm" color="blue.600">
          Back to runs
        </Link>
      </Flex>

      {isLoading && <Loader />}
      {isError && <ErrorState message="Failed to load run." />}

      {run && (
        <>
          <SimpleGrid columns={[1, 3]} spacing={3} mb={4}>
            <Box borderWidth="1px" borderRadius="md" p={3} bg="white">
              <Text fontSize="sm" fontWeight="semibold" mb={1}>
                Status
              </Text>
              <Text fontSize="sm">{run.status}</Text>
            </Box>
            <Box borderWidth="1px" borderRadius="md" p={3} bg="white">
              <Text fontSize="sm" fontWeight="semibold" mb={1}>
                Compliance
              </Text>
              <Text fontSize="sm">
                {run.compliance_score != null
                  ? `${Math.round(run.compliance_score * 100)}%`
                  : '—'}
              </Text>
            </Box>
            <Box borderWidth="1px" borderRadius="md" p={3} bg="white">
              <Text fontSize="sm" fontWeight="semibold" mb={1}>
                Duration
              </Text>
              <Text fontSize="sm">
                {run.finished_at
                  ? `${Math.round(
                      (new Date(run.finished_at).getTime() -
                        new Date(run.started_at).getTime()) /
                        1000
                    )} s`
                  : 'In progress'}
              </Text>
            </Box>
          </SimpleGrid>

          <Box borderWidth="1px" borderRadius="md" p={3} bg="white" mb={4}>
            <Text fontSize="sm" fontWeight="semibold" mb={2}>
              Findings
            </Text>
            <Text fontSize="xs" color="gray.500" mb={2}>
              TODO: Replace with richer findings component.
            </Text>
            <VStack
              align="stretch"
              spacing={1}
              maxH="180px"
              overflowY="auto"
              fontSize="xs"
            >
              {run.findings.map((f) => (
                <Text key={f.finding_id}>
                  [{f.severity}] {f.file_path}:{f.line} — rule {f.rule_id} (
                  {f.status})
                </Text>
              ))}
            </VStack>
          </Box>

          <Box borderWidth="1px" borderRadius="md" p={3} bg="white">
            <Text fontSize="sm" fontWeight="semibold" mb={2}>
              Artifacts
            </Text>
            <VStack align="stretch" spacing={1} fontSize="xs">
              {run.artifacts.map((a) => (
                <Link key={a.artifact_id} href={a.uri} target="_blank">
                  {a.type} ({a.checksum.slice(0, 8)}…)
                </Link>
              ))}
            </VStack>
          </Box>
        </>
      )}
    </Box>
  );
};

export default RunDetailPage;