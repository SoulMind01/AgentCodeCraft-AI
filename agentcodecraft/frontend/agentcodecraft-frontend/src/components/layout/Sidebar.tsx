import React from 'react';
import { NavLink } from 'react-router-dom';
import { Box, VStack, Text, Button } from '@chakra-ui/react';

const Sidebar: React.FC = () => {
  return (
    <Box
      as="aside"
      w="240px"
      bg="white"
      borderRightWidth="1px"
      borderColor="gray.200"
      p={4}
    >
      <Text fontSize="lg" fontWeight="semibold" mb={4}>
        AgentCodeCraft
      </Text>
      <VStack align="stretch" spacing={2}>
        <Button
          as={NavLink}
          to="/runs"
          variant="ghost"
          justifyContent="flex-start"
          _activeLink={{ bg: 'gray.900', color: 'white' }}
        >
          Runs
        </Button>
        <Button
          as={NavLink}
          to="/new"
          variant="ghost"
          justifyContent="flex-start"
          _activeLink={{ bg: 'gray.900', color: 'white' }}
        >
          New Run
        </Button>
        <Button
          as={NavLink}
          to="/policies"
          variant="ghost"
          justifyContent="flex-start"
          _activeLink={{ bg: 'gray.900', color: 'white' }}
        >
          Policies
        </Button>
        <Button
          as={NavLink}
          to="/settings"
          variant="ghost"
          justifyContent="flex-start"
          _activeLink={{ bg: 'gray.900', color: 'white' }}
        >
          Settings
        </Button>
      </VStack>
    </Box>
  );
};

export default Sidebar;