import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Flex, Heading, Button } from '@chakra-ui/react';
import { useRuns } from '../api/hooks';
import Loader from '../components/shared/Loader';
import ErrorState from '../components/shared/ErrorState';
import RunTable from '../components/runs/RunTable';

const DashboardPage: React.FC = () => {
  const { data: runs, isLoading, isError } = useRuns();

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={4}>
        <Heading as="h1" size="md">
          Runs
        </Heading>
        <Button
          as={RouterLink}
          to="/new"
          colorScheme="gray"
          variant="solid"
          size="sm"
        >
          New Run
        </Button>
      </Flex>

      {isLoading && <Loader />}
      {isError && <ErrorState message="Failed to load runs." />}
      {runs && <RunTable runs={runs} />}
    </Box>
  );
};

export default DashboardPage;