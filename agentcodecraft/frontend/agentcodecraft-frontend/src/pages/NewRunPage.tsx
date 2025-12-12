import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Heading,
  Stack,
  HStack,
  Button,
  FormControl,
  FormLabel,
  Select,
  Checkbox,
  Text,
  VStack,
  useToast,
} from '@chakra-ui/react';
import { usePolicies, useStartRefactor } from '../api/hooks';
import Loader from '../components/shared/Loader';
import ErrorState from '../components/shared/ErrorState';
import type { StartRefactorPayload } from '../api/types';

const NewRunPage: React.FC = () => {
  const { data: policies, isLoading, isError } = usePolicies();
  const startRefactor = useStartRefactor();
  const navigate = useNavigate();
  const toast = useToast();

  const [language, setLanguage] = useState<'python' | 'terraform'>('python');
  const [mode, setMode] = useState<'auto' | 'suggest'>('suggest');
  const [runTests, setRunTests] = useState(true);
  const [selectedPolicyIds, setSelectedPolicyIds] = useState<string[]>([]);
  const [files, setFiles] = useState<{ path: string; content: string }[]>([]);

  const handleStart = async () => {
    if (!files.length || !selectedPolicyIds.length) {
      toast({
        status: 'warning',
        description: 'Please add at least one file and select a policy.',
      });
      return;
    }

    const payload: StartRefactorPayload = {
      language,
      mode,
      run_tests: runTests,
      files,
      policy_ids: selectedPolicyIds,
    };

    try {
      const result = await startRefactor.mutateAsync(payload);
      navigate(`/runs/${result.run_id}`);
    } catch {
      toast({
        status: 'error',
        description: 'Failed to start run.',
      });
    }
  };

  const addStubFile = () => {
    setFiles([
      {
        path: 'example.py',
        content: 'print("hello from stub")',
      },
    ]);
  };

  return (
    <Box maxW="720px">
      <Heading as="h1" size="md" mb={4}>
        New Run
      </Heading>

      <Stack spacing={4}>
        <Box>
          <FormLabel fontSize="sm">Language</FormLabel>
          <HStack spacing={2}>
            <Button
              size="sm"
              variant={language === 'python' ? 'solid' : 'outline'}
              colorScheme="gray"
              onClick={() => setLanguage('python')}
            >
              Python
            </Button>
            <Button
              size="sm"
              variant={language === 'terraform' ? 'solid' : 'outline'}
              colorScheme="gray"
              onClick={() => setLanguage('terraform')}
            >
              Terraform
            </Button>
          </HStack>
        </Box>

        <FormControl>
          <FormLabel fontSize="sm">Mode</FormLabel>
          <Select
            size="sm"
            value={mode}
            onChange={(e) => setMode(e.target.value as 'auto' | 'suggest')}
          >
            <option value="suggest">Suggest only (do not apply)</option>
            <option value="auto">Auto apply (experimental)</option>
          </Select>
        </FormControl>

        <FormControl display="flex" alignItems="center">
          <Checkbox
            isChecked={runTests}
            onChange={(e) => setRunTests(e.target.checked)}
            size="sm"
          >
            Run tests / validation
          </Checkbox>
        </FormControl>

        <Box>
          <FormLabel fontSize="sm">Policies</FormLabel>
          {isLoading && <Loader message="Loading policies..." />}
          {isError && <ErrorState message="Failed to load policies." />}
          {policies && (
            <Box
              borderWidth="1px"
              borderRadius="md"
              p={2}
              maxH="220px"
              overflowY="auto"
              bg="white"
            >
              <VStack align="stretch" spacing={1}>
                {policies.map((p) => {
                  const selected = selectedPolicyIds.includes(p.policy_id);
                  return (
                    <Checkbox
                      key={p.policy_id}
                      isChecked={selected}
                      size="sm"
                      onChange={(e) => {
                        setSelectedPolicyIds((prev) =>
                          e.target.checked
                            ? [...prev, p.policy_id]
                            : prev.filter((id) => id !== p.policy_id)
                        );
                      }}
                    >
                      <HStack justify="space-between">
                        <Text fontSize="sm">{p.name}</Text>
                        <Text fontSize="xs" color="gray.500">
                          {p.language} v{p.version}
                        </Text>
                      </HStack>
                    </Checkbox>
                  );
                })}
              </VStack>
            </Box>
          )}
        </Box>

        <Box>
          <FormLabel fontSize="sm">Files</FormLabel>
          <Text fontSize="xs" color="gray.500" mb={1}>
            TODO: Replace with drag-and-drop uploader. Using stub file for now.
          </Text>
          <Button variant="link" size="sm" colorScheme="blue" onClick={addStubFile}>
            Add example stub file
          </Button>
          <VStack align="stretch" spacing={1} mt={2}>
            {files.map((f) => (
              <Text key={f.path} fontSize="xs" color="gray.600">
                {f.path} ({f.content.length} chars)
              </Text>
            ))}
          </VStack>
        </Box>

        <Button
          colorScheme="gray"
          size="sm"
          alignSelf="flex-start"
          onClick={handleStart}
          isDisabled={
            startRefactor.isPending || !files.length || !selectedPolicyIds.length
          }
          isLoading={startRefactor.isPending}
          loadingText="Starting…"
        >
          Start Refactor
        </Button>
      </Stack>
    </Box>
  );
};

export default NewRunPage;