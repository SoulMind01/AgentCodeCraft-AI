import React from 'react';
import { Flex, Text, HStack, IconButton, useColorMode } from '@chakra-ui/react';
import { MoonIcon, SunIcon } from '@chakra-ui/icons';

const Topbar: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Flex
      as="header"
      h="56px"
      borderBottomWidth="1px"
      borderColor="gray.200"
      bg="white"
      px={4}
      align="center"
      justify="space-between"
    >
      <Text fontSize="sm" color="gray.600">
        Policy-driven refactoring dashboard
      </Text>
      <HStack spacing={4}>
        <IconButton
          aria-label="Toggle color mode"
          size="sm"
          onClick={toggleColorMode}
          icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
        />
        <Text fontSize="sm" color="gray.700">
          <Text as="span" color="gray.500" mr={1}>
            Signed in as
          </Text>
          <Text as="span" fontWeight="semibold">
            demo@user
          </Text>
        </Text>
      </HStack>
    </Flex>
  );
};

export default Topbar;