import { Button, Heading, Box, Spinner, Center, Text, Input } from "@chakra-ui/react"
import { CheckIcon, CloseIcon, SmallAddIcon } from "@chakra-ui/icons"
import { useEffect, useState } from "react"
import Layout from "../layout/layout"
import styles from '../styles/Home.module.scss'


const ShoppingList = () => {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [newTask, setNewTask] = useState("")

  const fetchData = async () => {
    const res = await fetch(process.env.NEXT_PUBLIC_API_URL + '/tasklist/');
    let data = await res.json()
    setTasks(data.tasks)
    setLoading(false)
  }

  useEffect(() => {
    // call the function
    fetchData()
      // make sure to catch any error
      .catch(console.error);
  }, [])

  const createTask = async (e) => {
    e.preventDefault()
    try {
      let res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/tasklist/create", {
        method: "POST",
        body: JSON.stringify({
          content: newTask
        }),
      });
      if (res.status === 200) {
        setNewTask("");
        fetchData()
      }
    } catch (err) {
      console.log(err);
    }
  }

  function removeObjectWithId(arr, id) {
    const objWithIdIndex = arr.findIndex((obj) => obj.id === id);
    arr.splice(objWithIdIndex, 1);
    return arr;
  }

  const deleteTask = async (id) => {
    try {
      // Remove manually so that it is quick!
      let remaining = removeObjectWithId([...tasks], id);
      setTasks(remaining)
      let res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/tasklist/delete/" + id);
      if (res.status === 200) {
        fetchData()
      }
    } catch (err) {
      console.log(err);
    }
  }

  const updateTask = async (id, completed) => {
    try {
      let res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/tasklist/update/" + id, {
        method: "POST",
        body: JSON.stringify({
          completed
        })
      });
      if (res.status === 200) {
        fetchData();
      }
    } catch (err) {
      console.log(err);
    }
  }

  return (
    <Layout metas={{title: "Shopping List"}}>
      <Box w='xl' maxW={'100%'} my={5} p={2}>
        <Heading>Shopping List</Heading>
        <Text my={2}>Ayo pick this up</Text>
        <form onSubmit={createTask} method="POST">
          <Box display={'flex'} mb={2}>
            <Input
              type="text"
              name="content"
              id="content"
              bg={'white'}
              onChange={(e) => setNewTask(e.target.value)}
              value={newTask}
              placeholder={"New item"}
              marginRight={1}
            />
            <Button type="submit">Create</Button>
          </Box>
        </form>
        {loading ?
        <>
        <Center>
          <Spinner m={6} size='lg'/>
        </Center>
        </>:
        <>
        <Box w={'600px'} maxW={'100%'} bg={'white'} boxShadow={'md'} borderRadius={'10px'} p={2} px={4}>
          {tasks.map((task) => (
            <Box key={task.id} display={'flex'} justifyContent={'space-between'} py={2} borderBottom={'1px solid'} borderColor={'gray.400'}>
              <Text>
                {
                  task.completed ?
                  <CheckIcon marginRight={2}/>
                  :
                  <CloseIcon w={3} marginRight={3}/>
                }
                {task.content}
              </Text>
              <Box>
                {task.completed ?
                <>
                  <Button colorScheme='gray' size={'xs'} onClick={() => updateTask(task.id, false)} mx={1}>Undo</Button>
                </>:
                <>
                  <Button colorScheme='teal' size={'xs'} leftIcon={<CheckIcon/>} onClick={() => updateTask(task.id, true)} mx={1}>Complete</Button>
                </>}
                <Button colorScheme='red' size={'xs'} mx={1} onClick={() => deleteTask(task.id)}><CloseIcon /></Button>
              </Box>
            </Box>
          ))}
        </Box>
        </>
      }
      </Box>
    </Layout>
  )
}

export default ShoppingList;
