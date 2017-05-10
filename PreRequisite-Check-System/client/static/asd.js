<script type="text/javascript">
    function testJS()
    {

        var b = document.getElementById('username').value,
        url = '/Users/Abhishek/Sem1Projects/CMPE273Project/PrereqCheckSystem/client/templates/index.html?name=' + encodeURIComponent(b);

        document.location.href = url;

    }
</script>