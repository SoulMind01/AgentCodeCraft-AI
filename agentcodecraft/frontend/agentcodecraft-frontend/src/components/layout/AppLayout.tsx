import React from 'react';
import { Flex, Box } from '@chakra-ui/react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <Flex minH="100vh" bg="gray.50">
      <Sidebar />
      <Flex direction="column" flex="1">
        <Topbar />
        <Box as="main" p={4} flex="1">
          {children}
        </Box>
      </Flex>
    </Flex>
  );
};

export default AppLayout;