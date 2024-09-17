using MySql.Data.MySqlClient;
using System.Collections.Generic;
using System.Data;
using System.Threading.Tasks;

namespace WhedNamespace
{
    public class DatabaseContext
    {
        private readonly string _connectionString;

        public DatabaseContext(string connectionString)
        {
            _connectionString = connectionString;
        }

        public async Task<List<string>> GetTestDataAsync()
        {
            List<string> data = new List<string>();

            using (MySqlConnection conn = new MySqlConnection(_connectionString))
            {
                await conn.OpenAsync();

                using (MySqlCommand cmd = new MySqlCommand("SELECT OrgID, OrgName FROM whed_org", conn))
                {
                    using (var reader = await cmd.ExecuteReaderAsync())
                    {
                        while (await reader.ReadAsync())
                        {
                            data.Add(reader.GetString("OrgID"));
                            data.Add(reader.GetString("OrgName"));
                        }
                    }
                }
            }

            return data;
        }
    }
}